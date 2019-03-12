import sys
import os

from lxml import etree

def printf(format, *args):
    sys.stdout.write(format % args)

#dir_path = os.path.dirname(os.path.realpath(__file__)) 

printf ("Block Name\tKey\tSink\tSource\tType(s)\tCategory\t\tParam(s)\n")

for rootDir, dirs, files in os.walk(sys.argv[1]): 
    for curFile in files:  
        if curFile.endswith('.xml'): 
            xmlFilePath=rootDir+"/"+curFile
            xmlFile = open(xmlFilePath, "r")
            #print (xmlFilePath)
            root = etree.parse(xmlFile).getroot() 
            if (root.tag == "block"):
                blockKey=""
                sink=""
                source=""
                types=""
                blockName=""
                params=""
                category=""

                for child in root:
                    if (child.tag == "key"):
                        blockKey = child.text
                    elif (child.tag == "name"):
                        blockName = child.text
                    elif (child.tag == "sink"):
                        sink = child[1].text
                        for subChild in child.iter("vlen"):
                            sink = sink + "<" + subChild.text + ">"
                        for subChild in child.iter("nports"):
                            sink = sink + "[" + subChild.text + "]"
                    elif (child.tag == "source"):
                        source = child[1].text
                        for subChild in child.iter("vlen"):
                            source = source + "<" + subChild.text + ">"
                        for subChild in child.iter("nports"):
                            source = source + "[" + subChild.text + "]"
                    elif (child.tag == "param"):
                        # Check whether the param has option..
                       # bool hasOption=False
#                        if any (True for opt in child.iter("option")):
#                            print (child.tag, "has children")
                        paramName=""
                        paramType=""
                        paramValue=""
                        for subChild in child:
                            if (subChild.tag == "key"):
                                paramName = subChild.text
                            elif (subChild.tag == "value"):
                                paramValue = subChild.text
                            elif (subChild.tag == "type"):
                                paramType = subChild.text
                                if (paramType == "enum"):
                                    paramType=""
                                    for subSubChild in subChild.itersiblings():
                                        if (subSubChild.tag == "option"):
                                            for key in subSubChild.iter("key"):
                                                paramType = paramType + key.text+","
                        #print ("param found: [", paramName, " - ", paramType, "]")
                        if (paramName == "type"):
                            types=paramType
                        else:
                            params = params + "\t" + paramName+":"+paramType
                            if paramValue:
                                params = params + " ("+paramValue+")"
                    elif (child.tag == "category"):
                        category = child.text
                    elif (child.tag == "import" or child.tag == "make" or child.tag == "callback" or
                            child.tag == "doc" or child.tag == "var_value" or child.tag == "var_make" or
                            child.tag == "category" or child.tag == "check" or child.tag == "param_tab_order" or
                            child.tag == "flags" or str(child.tag).startswith('<') or str(child.tag).startswith('bus')):
                        continue
                    else:
                        print ("Unexpected element: ", child.tag)


                #    for subChild in child.iter():
                #        print subChild.tag
                printf ("%s\t%s\t%s\t%s\t%s\t%s\t%s\n", blockName.encode('utf8'), blockKey, sink, source, types, category, params.encode('utf8'))




