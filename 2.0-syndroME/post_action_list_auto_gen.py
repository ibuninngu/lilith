def auto_gen():
    import glob
    action_list_directory = "./sl_functions/http"
    functions_directory = action_list_directory + "/post_actions"
    path = "import "+functions_directory[2:].replace("/",".")
    imports = ""
    hashmaps = "post_list = {"
    print(">>> auto gen...")
    for a in glob.glob(functions_directory+"/*.py"):
        mod_name = a[a.find("\\")+1:-3]
        imports += path + "." + mod_name + " as " + mod_name + "\n"
        hashmaps += "\"/" + mod_name + ".post\":" + mod_name + "." + mod_name + ","
        print(">>>",mod_name)
    hashmaps = hashmaps[:-1] + "}"
    f = open(action_list_directory+"/post_action_list.py","w")
    f.write(imports+hashmaps)
    f.close()