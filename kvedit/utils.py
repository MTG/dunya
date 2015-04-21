from kvedit.models import Field, Item, Category

def upload_kvdata(cat_name, source_file_type, items_dic):
    category, created = Category.objects.get_or_create(name=cat_name, defaults={source_file_type: source_file_type})
    if category.source_file_type != source_file_type:
        category.source_file_type = source_file_type
        category.save()
    # Select the items with the same id
    existing_items = Item.objects.filter(ref__in=items_dic.keys(), category=category)
    for item in existing_items:
        existing_keys = []
        for field in items_dic[item.ref]:
            old_field = item.fields.filter(key=field.key)
            existing_keys.append(field.key)
            # If the old Fields has the same key, override the value unless they hass already been modified
            if len(old_field) == 1 and old_field[0].value != field.value and not old_field[0].modified:
                old_field[0].value = field.value
                old_field[0].save()
            elif len(old_field) == 0:
                field.item = item
                field.save()
        item.fields.exclude(key__in=existing_keys, modified=False).delete()
        item.reverify = True
        item.save()
        items_dic[item.ref]

        del items_dic[item.ref]
    # Save the new Fields and Items
    for ref, fields in items_dic.iteritems():
        item = Item(ref=ref)
        item.category = category
        item.save()
        for field in fields:
            field.item = item
            field.save()
