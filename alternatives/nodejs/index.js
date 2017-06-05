require('format-unicorn');
var fs = require('fs');
var path = require('path');
var parseArgs = require('minimist');
var finalhandler = require('finalhandler');
var http = require('http');
var ip = require('ip');
var serveStatic = require('serve-static');
var MediaRendererClient = require('upnp-mediarenderer-client');

// Arguments
var argv = parseArgs(process.argv.slice(2),
                     opts = {'default': {
                                 'folder'     : '/var/tmp/nano-dlna',
                                 'metadata'   : 'data/metadata-video_subtitle.xml',
                                 'file_video' : 'video.avi',
                                 'file_sub'   : 'video.srt',
                                 'file_cover' : 'cover.jpg',
                             }
                     });

// HTTP media streaming server
var http_port = 3000;
var streaming_serve = serveStatic(argv['folder']);
var streaming_server = http.createServer(function(req, res) {
    var done = finalhandler(req, res);
    streaming_serve(req, res, done);
})
streaming_server.listen(http_port);

// URIs available
var uri_base  = 'http://' + ip.address() + ':' + http_port + '/';
var uris = {
    'uri_video'  : uri_base + argv['file_video'],
    'uri_sub'    : uri_base + argv['file_sub'],
    'uri_cover'  : uri_base + argv['file_cover'],
    'type_video' : path.extname(argv['file_video']).split('.')[1].toLowerCase(),
    'type_sub'   : path.extname(argv['file_sub']).split('.')[1].toLowerCase()
};

// DLNA metadata
var metadata_raw = fs.readFileSync(argv['metadata'], {'encoding': 'utf8'});
var metadata_pretty = metadata_raw.formatUnicorn(uris);
var metadata = metadata_pretty.replace(/\s{2,}/g, ' ').replace(/> </g, '><').trim();
console.log(metadata_pretty);

//// DLNA connection
//var dlna_client = new MediaRendererClient(argv['media-renderer-url']);
//dlna_client.load(uris['uri_video'], { autoplay: true, metadata: metadata }, function(err, result) {
//    if(err) throw err
//    console.log('playing ...')
//});

