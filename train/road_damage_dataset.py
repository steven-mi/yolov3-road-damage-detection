import xml.etree.ElementTree as ET
import pickle
import os
from os import listdir, getcwd
from os.path import join

govs=["Adachi", "Chiba", "Muroran", "Ichihara", "Sumida", "Nagakute", "Numazu"]
sets=["train", "val"]

damageTypes=["D00", "D01", "D10", "D11", "D20", "D40"]
# "D43", "D44"]

def convert(size, box):
    dw = 1./size[0]
    dh = 1./size[1]
    x = (box[0] + box[1])/2.0
    y = (box[2] + box[3])/2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)


def convert_annotation(gov, image_id):
    in_file = open('RoadDamageDataset/%s/Annotations/%s.xml'%(gov, image_id))
    out_file = open('RoadDamageDataset/%s/labels/%s.txt'%(gov, image_id), 'w')
    tree=ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    for obj in root.iter('object'):
        cls = obj.find('name').text
        if cls not in damageTypes:
            continue
        cls_id = damageTypes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = convert((w,h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')
        
for image_set in sets:
    list_file = open('%s.txt'%(image_set), 'w')
    for gov in govs:
        if not os.path.exists('RoadDamageDataset/%s/labels/'%(gov)):
            os.makedirs('RoadDamageDataset/%s/labels/'%(gov))
        image_ids = open('RoadDamageDataset/%s/ImageSets/Main/%s.txt'%(gov, image_set)).read().strip().split()
        for image_id in image_ids:
            list_file.write('RoadDamageDataset/%s/JPEGImages/%s.jpg\n'%(gov, image_id))
            convert_annotation(gov, image_id)
    list_file.close()
