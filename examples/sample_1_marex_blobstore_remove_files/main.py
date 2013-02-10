#!/usr/bin/python
# -*- coding: utf-8 -*-
import webapp2
from  google.appengine.api import files
from  google.appengine.ext import blobstore
from marex import blobstore as marex_blobstore

config = {}
routes = [
    webapp2.Route("/", "main.MainHandler", "index", handler_method="index", methods=['GET']),
    webapp2.Route("/create", "main.MainHandler", "create_file", handler_method="create_file", methods=['POST']),
    webapp2.Route("/remove", "main.MainHandler", "remove_files", handler_method="remove_files", methods=['POST']),
]

app = webapp2.WSGIApplication(routes=routes, config=config, debug=True)

class MainHandler(webapp2.RequestHandler):
    def index(self):
        file_count = 0
        content = "<!DOCTYPE html>\n"
        content += "<html>\n<head>\n<title>marex sample 1 - blobstore remove files</title>\n"
        content += "<script>function toggle_selection(){var checkCount=0;var checkboxes=document.getElementsByName(\"blob\");for(var i=0;i<checkboxes.length;++i){if(checkboxes[i].checked)checkCount+=1;}var checkValue=(checkCount!=checkboxes.length);for(var i=0;i<checkboxes.length;++i){checkboxes[i].checked=checkValue;}return false;}</script>\n"
        content += "</head>\n<body>\n"
        content += "<div style=\"clear:both\" id=\"createFileSection\">\n"
        content += "<h2>Create BlobStore File</h2>\n"
        content += "<form action=\"{0}\" method=\"POST\">\n".format(self.uri_for("create_file"))
        content += "<label for=\"filename\" style=\"display: block; width: 150px\">Filename:</label>\n"
        content += "<input type=\"text\" name=\"filename\" id=\"filename\"/ style=\"width: 225px\">"
        content += "<button type=\"submit\" style=\"width: 125px\">Create</button>\n"
        content += "<br />\n"
        content += "<label for=\"content\" style=\"display: block; width: 150px\">Content:</label>\n"
        content += "<textarea name=\"content\" id=\"content\" style=\"width: 350px; height: 80px\"></textarea>\n"
        content += "<br />\n"
        content += "</form>\n"
        content += "</div>\n"
        content += "<div style=\"clear:both\" id=\"removeFilesSection\">\n"
        content += "<h2>BlobStore Content</h2>\n"
        for blob_info in blobstore.BlobInfo.all():
            if file_count == 0:
                content += "<form action=\"{0}\" method=\"POST\">\n".format(self.uri_for("remove_files"))
                content += "<button type=\"button\" style=\"width: 50px\" onclick=\"toggle_selection()\">All</button>\n"
                content += "<button type=\"submit\" name=\"button\" value=\"sel\" style=\"width: 125px\">Remove Selected</button>\n"
                content += "<button type=\"submit\" name=\"button\" value=\"all\" style=\"width: 125px\">Remove All Files</button>\n"
            file_count += 1
            content += "<br /><input type=\"checkbox\" name=\"blob\" id=\"blob_{0}\" value=\"{0}\"><label for=\"blob_{0}\"><strong>{1}</strong> <em>({2} bytes)</em></label></input>".format(str(blob_info.key()), blob_info.filename, blob_info.size)
        if file_count > 0:
            content += "\n</form>\n"
        else:
            content += "<span style=\"background-color: lightcoral\">BlobStore is Empty!</span>"
        content += "</div>\n"
        content += "</body>\n</html>\n"
        self.response.write(content)

    def create_file(self):
        filename = "whatever.blob"
        content = "Lobster ALL the Fetish!\n"*100
        filename_sent = self.request.get("filename", filename)
        if filename_sent != "":
            filename = filename_sent
        content_sent = self.request.get("content", content)
        if content_sent != "":
            content = content_sent

        file_name = files.blobstore.create("text/plain", filename)
        with files.open(file_name, "a") as stream:
            stream.write(content)

        files.finalize(file_name)
        self.redirect_to("index")

    def remove_files(self):
        button = self.request.get("button")
        blobs = []
        if button == "sel":
            # remove selected
            blobs = self.request.get_all("blob")
        elif button == "all":
            # remove all
            blobs = blobstore.BlobInfo.all()
        else:
            # dafuq?!
            pass
        marex_blobstore.remove_files(*blobs, ignore_errors=True)
        self.redirect_to("index")
