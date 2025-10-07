import sys
sys.stdout = open('output.log', 'w')

path = r'D:\PipeZer'
sys.path.append(path)

from Packages.apps.houdini.ui.houdini_class import HoudiniPipeZer
ui = HoudiniPipeZer()
