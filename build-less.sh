map=''

while getopts "h?m" opt; do
    case "$opt" in
    h|\?)
        echo "generate css files from less files"
        echo "usage: $0 [-m]"
        echo "   -m: generate source maps"
        exit 0
        ;;
    m)  map='--source-map'
        ;;
    esac
done


./node_modules/.bin/lessc carnatic/static/carnatic/css/main.less carnatic/static/carnatic/css/main.css $map
./node_modules/.bin/lessc carnatic/static/carnatic/css/recording.less carnatic/static/carnatic/css/recording.css $map
./node_modules/.bin/lessc carnatic/static/carnatic/css/pages.less carnatic/static/carnatic/css/pages.css $map
./node_modules/.bin/lessc makam/static/makam/css/main.less makam/static/makam/css/main.css $map
./node_modules/.bin/lessc makam/static/makam/css/recording.less makam/static/makam/css/recording.css $map
./node_modules/.bin/lessc makam/static/makam/css/pages.less makam/static/makam/css/pages.css $map
