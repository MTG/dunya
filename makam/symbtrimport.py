#!/usr/bin/env python

## Import the SymbTr repository into the dunya docserver
## Requires pycompmusic

# Delete symbtr mapping
# Run in a django shell
def delete_mapping():
    import makam.models
    makam.models.SymbTr.objects.all().delete()

# Create symbtr mapping
# Run in a django shell
def create_mapping():
    import json
    import makam.models
    data = json.load(open("symbTr_mbid.json"))
    for d in data:
        uu = d["uuid"]["mbid"]
        makam.models.SymbTr.objects.create(name=d["name"], uuid=uu)

# Delete symbtr docserver collection, and rm the files
# Run in a django shell
def delete_documents():
    import docserver.models
    import json
    data = json.load(open("/homedtic/aporter/symbTr_mbid.json"))

    collection = docserver.models.Collection.objects.get(slug='makam-symbtr')
    documents = collection.documents.all()
    docids = [d.external_identifier for d in documents]
    sids = [s["uuid"]["mbid"] for s in data]
    symbtr = {s["uuid"]["mbid"]: s["name"] for s in data}

    new = set(sids)-set(docids)
    toremove = set(docids)-set(sids)

    for n in new:
        doc, created = docserver.models.Document.objects.get_or_create(external_identifier=n,
                defaults={"title": symbtr[n]})
        collection.documents.add(doc)

    slugs = [u'symbtrtxt', u'symbtrmidi', u'symbtrpdf', u'symbtrxml', u'symbtrmu2']
    sfts = docserver.models.SourceFileType.objects.filter(slug__in=slugs)
    for r in toremove:
        doc = collection.documents.get(external_identifier=r)
        for sf in doc.sourcefiles.filter(file_type__in=sfts):
            rmtree(sf.fullpath)
            sf.delete()
        collection.documents.remove(doc)
        if doc.sourcefiles.count() == 0:
            doc.delete()

    for mbid, title in symbtr.items():
        doc = collection.documents.get(external_identifier=mbid)
        doc.title = title
        doc.save()

def rmtree(path):
    if os.path.exists(path):
        os.unlink(path)
    parts = path.split("/")
    path = "/" + os.path.join(*parts[:-1])
    while len(os.listdir(path)) == 0:
        os.rmdir(path)
        parts = path.split("/")
        path = "/" + os.path.join(*parts[:-1])

# Create and upload docserver files
# Run in pycompmusic
def upload_symbtr(symbtr_file="/home/alastair/SymbTr/symbTr_mbid.json"):
    import compmusic.dunya
    import compmusic.dunya.docserver
    import time
    import json
    import os
    compmusic.dunya.set_token("")
    dir_slug = {"midi": "symbtrmidi"
              , "mu2": "symbtrmu2"
              , "MusicXML": "symbtrxml"
              , "txt": "symbtrtxt"
              , "SymbTr-pdf": "symbtrpdf"}

    data = json.load(open(symbtr_file))
    mbid_file = {s["uuid"]["mbid"]: s["name"] for s in data}

    for d, sl in dir_slug.items():
        ext = sl.replace("symbtr", "")[:3]
        count = len(mbid_file)
        for i, (mbid, name) in enumerate(mbid_file.items(), 1):
            filename = os.path.join(d, "%s.%s" % (name, ext))
            print "%s) %s/%s: %s (%s)" % (sl, i, count, mbid, name)
            compmusic.dunya.docserver.add_sourcetype(mbid, sl, filename)
            time.sleep(0.1) 

def retrive_git_changes():
    '''This method gets all changes from git and creates a file with the same 
    format as symbTr_mbid.json with the modified files, then calls 
    upload_symbtr method with this file to upload the modified files.
    
    Then calls delete_documents which deletes the documets that are not in the 
    original symbTr_mbid.json file.
    
    Finally calls delete_mappings and create_mappings which deletes all entries
    on the database from the Symbtr table and creates all again.
    
    Note: This method should be run from django shell.'''
    import json
    import os
    import docserver.models
    import git
    
    collid = ''
    git_dir = ''
    
    c = docserver.models.Collection.objects.get(collectionid=collid)
    c_data = json.loads(c.data)
    last = c_data['last_commit']
           
    dir_slug = {"midi": "symbtrmidi"
              , "mu2": "symbtrmu2"
              , "MusicXML": "symbtrxml"
              , "txt": "symbtrtxt"
              , "SymbTr-pdf": "symbtrpdf"}

    data = json.load(open(os.path.join(git_dir, "symbTr_mbid.json")))
    mbid_file = {s["name"]: s["uuid"]["mbid"] for s in data}

    g = git.cmd.Git(git_dir)
    differ = g.diff(last, '--name-only').split("\n")
    to_add = []
    to_remove = []
    for i in differ:
        score = i.split('/')
        if score[0] in dir_slug.keys() and len(score)>1:
            name = score[1].replace(dir_slug[score[0]],"").split(".")[0]
            if name in mbid_file:
                to_add.append({'name': name, 'uuid': {'mbid': mbid_file[name], 
                    'type': 'work'}})
    with open("/tmp/tmpsymbtr.json", "w") as outfile:
            json.dump(to_add, outfile, indent=4)
    
    print "Generated list of files to upload"
    print "Uploading Files"
    upload_symbtr("/tmp/tmpsymbtr.json")
    
    print "Deleting documents"
    delete_documents()
    
    print "Deleting Symbtr entries on database"
    delete_mapping()
    
    print "Creating Symbtr entries on database"
    create_mapping()
    
    c_data['last_commit'] = str(git.Repo(git_dir).head.commit)
    c.data = json.dumps(c_data)
    c.save()
    print "Done"

