import os 

def loadPrompt(filename):
    base_dir = os.path.dirname(os.path.dirname('PERSONAL_PROJECT'))
    promptPath = os.path.join(base_dir,"prompts",filename)
    
    with open(promptPath,'r') as file:
        return file.read()
    
