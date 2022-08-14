import subprocess
import os
import sys

#Usage: python colmap_runner.py --flags
#Flags: --colmap_exe_path "path" ==> Path to the colmap executeable.
#                                  > Defaults to looking for COLMAP.bat in a folder called COLMAP in the 
#                                  > folder this script is in
#
#       --image_path "path"      ==> Path to the folder containing the images for COLMAP's input
#                                  > Defailts to looking for a folder called "Images" in the folder 
#                                  > this script is in
#
#       --name "name"            ==> Name of the folder to be created to store the data for this instance
#                                  > of colmap.
#                                  > Defaults to "colmap_output"
#
#       --output_folder "path"   ==> Directory to where colmap will put its output.
#                                  > Defaults to the folder where this script is



#run_colmap function:
#
#creates a new folder called instance_name in output_path and fills it with the colmap data
#    generated by the exe at colmap_path with data from images_path
#
#returns a status code -

#    0 = Success
#    1 = Unspecified error
#    2 = FileExistsError; happens when you try to create data in an already existing folder
#    3 = FileNotFoundError; happens when you try to use an output folder that does not exist

def run_colmap(instance_name, output_path, colmap_path, images_path):
    ### Create a new folder to store our data
      # Add a / to the path if there isn't one
    if not output_path.endswith(("\\", "/")) and not instance_name.startswith(("\\", "/")):
        output_path = output_path + "/"
    instance_path = output_path + instance_name

    try:
        os.mkdir(instance_path)
    except FileExistsError:
        return 2
    except FileNotFoundError:
        return 3
    except:
        return 1

    #Creating a new database for colmap
    try:
        database_path = instance_path + "/database.db"
        subprocess.call([colmap_path, "database_creator", "--database_path", database_path])
        print("Created DB")
    except:
        return 1

    #Feature extracting
    try:
        subprocess.call([colmap_path, "feature_extractor","--SiftExtraction.use_gpu=true","--ImageReader.single_camera=1", "--database_path", database_path, "--image_path", images_path])
        print("Features Extracted")
    except:
        return 1

    #Feature matching
    try:
        print("Feature Matching")
        subprocess.call([colmap_path, "exhaustive_matcher","--SiftMatching.use_gpu=true", "--database_path", database_path])
    except:
        return 1

    #Generating model
    try:
        subprocess.call([colmap_path, "mapper", "--database_path", database_path, "--image_path", images_path, "--output_path", instance_path])
    except:
        return 1

    #Getting model as text
    try:
        # TODO: no longer works on windows fix file paths or run in docker
        subprocess.call([colmap_path, "model_converter", "--input_path", instance_path + r"/0", "--output_path", instance_path, "--output_type", "TXT"])
    except:
        return 1

    return 0


if __name__ == '__main__':
    #Default flags
    instance_name = "colmap_output"
    output_path = "./"
    colmap_path = r".\COLMAP\COLMAP.bat"
    images_path = r".\Images"

    #Parse flags
    #Flag format up top
    for i in range (len(sys.argv)):
        if i == 0:
            continue
        if sys.argv[i].startswith("--"):
            match sys.argv[i]:
                case "--output_folder":
                    output_path = sys.argv[i+1]
                case "--name":
                    instance_name = sys.argv[i+1]
                case "--colmap_exe_path":
                    colmap_path = sys.argv[i+1]
                case "--image_path":
                    images_path = sys.argv[i+1]
                case _:
                    print("ERROR: Unrecognized flag", sys.argv[i])
                    quit()

    #Run COLMAP :)
    status = run_colmap(instance_name, output_path, colmap_path, images_path)
    if status == 0:
        print("COLMAP ran successfully.")
    elif status == 1:
        print("ERROR: There was an unknown error running COLMAP")
    elif status == 2:
        print(f"ERROR: COLMAP - file {output_path}/{instance_name} already exists.")
    elif status == 3:
        print(f"ERROR: COLMAP - file {output_path} could not be found.")