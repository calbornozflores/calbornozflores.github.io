import os
import re
import sys
import json
import codecs
import shutil
import argparse
import subprocess

# read the text file poke_gallery/script/gallery.js
def read_gallery_js():
    gallery_js = open('poke_gallery/script/gallery.js', 'r')
    gallery_js_content = gallery_js.readlines()
    gallery_js.close()
    return gallery_js_content


def update_gallery_js(gallery_js_content, imageList):
    for i in range(len(gallery_js_content)):
        if re.search('var imageList', gallery_js_content[i]):
            gallery_js_content[i] = '    var imageList = ' + imageList + ';\n'
            break
    return gallery_js_content


script = read_gallery_js()

imageList = os.listdir('poke_gallery/images')
imageList_str = "[" + ", ".join(['"' + image + '"' for image in imageList]) + "]"

updaed_script = update_gallery_js(script, imageList_str)

gallery_js = open('poke_gallery/script/gallery.js', 'w')
gallery_js.writelines(updaed_script)
gallery_js.close()

print('imageList updated')