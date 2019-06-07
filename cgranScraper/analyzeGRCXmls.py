import sys
import os
import argparse

from lxml import etree

def printf(format, *args):
    sys.stdout.write(format % args)

dir_path = os.path.dirname(os.path.realpath(__file__)) 

#printf ("Block Name\tKey\tSink\tSource\tType(s)\tCategory\t\tParam(s)\n")

blockFrequencies=dict()
grcToBlocks=dict()

# defined command line options
# this also generates --help and error handling
CLI=argparse.ArgumentParser()
CLI.add_argument(
    "--blockFilters", 
   nargs="*", 
   type=str,
)
CLI.add_argument(
    "--grcFolder", 
   nargs=1, 
   type=str,
   required=True,
)
#CLI.add_argument(
#    "--output", 
#   nargs=1, 
#   type=str,
#   required=True,
#)
CLI.add_argument(
    "--mode", 
   nargs=1, 
   type=str,
   choices=["usageFreq", "proximityGraph"],
   required=True,
)




# parse the command line
args = CLI.parse_args()
# access CLI options
#print("filters: %r" % args.blockFilters)
#print("grcFolder: %r" % args.grcFolder)

for rootDir, dirs, files in os.walk(args.grcFolder[0]): 
    for curFile in files:  
        if curFile.endswith('.grc'): 
            xmlFilePath=rootDir+"/"+curFile
            xmlFile = open(xmlFilePath, "r")
            #print (xmlFilePath)
            root = etree.parse(xmlFile).getroot() 
        
            assert (root.tag == "flow_graph")
            grcToBlocks[xmlFile]=list()

            for block in root.iter("block"):
                #print "hey"
                blockKey=""
                sink=""
                source=""
                types=""
                blockName=""
                params=""
                category=""
                for child in block:
                    if (child.tag == "key"):
                        #print "found key.."
                        blockFiltered=False
                        for filterText in args.blockFilters:
                            if filterText in child.text:
                                blockFiltered=True
                        if blockFiltered==False:
                            if (child.text in blockFrequencies ):
                                blockFrequencies[child.text] += 1
                            else:
                                blockFrequencies[child.text] = 1
                            grcToBlocks[xmlFile].append(child.text)
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
                        pass
                        #print ("Unexpected element: ", child.tag)


                #    for subChild in child.iter():
                #        print subChild.tag
               # printf ("%s\t%s\t%s\t%s\t%s\t%s\t%s\n", blockName.encode('utf8'), blockKey, sink, source, types, category, params.encode('utf8'))

edges=dict()

for grcName in grcToBlocks:
    blockList = list(dict.fromkeys(grcToBlocks[grcName]))
    
    i=0
    j=0
    while (i < len(blockList)):
        j=i+1
        while (j < len(blockList)):
            edge=blockList[i]+" -- "+blockList[j]
            reverseEdge=blockList[j]+" -- "+blockList[i]
            if edge in edges:
                edges[edge] += 1
            elif reverseEdge in edges:
                edges[reverseEdge] += 1
            else:
                edges[edge] = 1
            j=j+1
        i=i+1    


if args.mode[0] == "usageFreq":
    for nodeItem in sorted(blockFrequencies.items(), key=lambda x: x[1], reverse=True) :
        print ("%s\t%s" % (nodeItem[0], nodeItem[1]))
 
elif args.mode[0] == "proximityGraph":
    print "graph g{"
    for nodeItem in sorted(blockFrequencies.items(), key=lambda x: x[1], reverse=True) :
        nodeLabel=nodeItem[0].replace('_',' ')
        print ("\t%s [label=\"%s\" freq=%s];" % (nodeItem[0], nodeLabel, nodeItem[1]))

    print " " 

    for edgeItem in sorted(edges.items(), key=lambda x: x[1], reverse=True) :
        print ("\t%s [weight=%s]" % (edgeItem[0], edgeItem[1]) )
        
    print "}"


