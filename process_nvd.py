import json
import pandas as pd
import os
import sys

nvd_master_json_file = ""

def cve_config_bootstrap():
    """Bootstrap configuration files"""
    
    print("\n***** Beginning processing of configuration files *****\n")
    
    app_config_file = "./config/app_config.json"
    user_config_file = "./config/user_config.json"
    
    if os.path.isfile(app_config_file):
        try:
            with open(app_config_file, 'r', encoding='utf-8') as app_config:
                app_config_obj = json.load(app_config)
        except Exception as e:
            sys.exit(f"Error accessing the application configuration file: {e}")
        else:
            print(f"Application configuration settings loaded from: {app_config_file}")
    
    if os.path.isfile(user_config_file):
        try:
            with open(user_config_file, 'r', encoding='utf-8') as user_config:
                user_config_obj = json.load(user_config)
        except Exception as e:
            sys.exit(f"Error accessing the user configuration file: {e}")
        else:
            print(f"User configuration settings loaded from: {user_config_file}")

    return app_config_obj, user_config_obj




def process_nvd_files(app_config: dict):
    impact_list = []
    impact_tuple = ()
    cve_count = 0
    cve_rejected = 0
    cve_no_cvss = 0
    


    nvd_data_files = []
    nvd_data_dir = app_config["NVD_DATA_DIR"]
    
    for nvd_file in app_config["NVD_DATA_FILES"]:
        nvd_data_files.append(nvd_data_dir+nvd_file)
        

    print(nvd_data_files)
    
    for nvd_file in nvd_data_files:
        
        try:
            with open(nvd_file, encoding="utf-8") as nvd_data:
                nvd_json = json.load(nvd_data)
                                
                for cve_data in nvd_json["CVE_Items"]:
                    cve_count += 1
                    
                    cve_id = cve_data["cve"]["CVE_data_meta"]["ID"]
                    cve_assigner = cve_data["cve"]["CVE_data_meta"]["ASSIGNER"]
                    description = cve_data["cve"]["description"]["description_data"][0]["value"]
                    
                    # print(f"{cve_data["cve"]["CVE_data_meta"]["ID"]}\n")
                    # print(f"{cve_data["cve"]["CVE_data_meta"]["ASSIGNER"]}\n")
                    # print(f"{cve_data["cve"]["description"]["description_data"][0]["value"]}\n")
                    
                    try:
                        cvss_keys = cve_data["impact"].keys()
                        if "baseMetricV3" in cvss_keys:
                            # print(f"{cve_data["impact"]["baseMetricV3"]["cvssV3"]}\n")
                            cvss_v3_version = cve_data["impact"]["baseMetricV3"]["cvssV3"]["version"]
                            cvss_v3_vectorString = cve_data["impact"]["baseMetricV3"]["cvssV3"]["vectorString"]
                            cvss_v3_attackVector = cve_data["impact"]["baseMetricV3"]["cvssV3"]["attackVector"]
                            cvss_v3_attackComplexity = cve_data["impact"]["baseMetricV3"]["cvssV3"]["attackComplexity"]
                            cvss_v3_privilegesRequired = cve_data["impact"]["baseMetricV3"]["cvssV3"]["privilegesRequired"]
                            cvss_v3_userInteraction = cve_data["impact"]["baseMetricV3"]["cvssV3"]["userInteraction"]
                            cvss_v3_baseSeverity = cve_data["impact"]["baseMetricV3"]["cvssV3"]["baseSeverity"]
                        elif "baseMetricV2" in cvss_keys:
                            # print(f"{cve_data["impact"]["baseMetricV2"]["cvssV2"]}\n")
                            cvss_v2_version = cve_data["impact"]["baseMetricV2"]["cvssV2"]["version"]
                            cvss_v2_vectorString = cve_data["impact"]["baseMetricV2"]["cvssV2"]["vectorString"]
                            cvss_v2_accessVector = cve_data["impact"]["baseMetricV2"]["cvssV2"]["accessVector"]
                            cvss_v2_accessComplexity = cve_data["impact"]["baseMetricV2"]["cvssV2"]["accessComplexity"]
                            cvss_v2_authentication = cve_data["impact"]["baseMetricV2"]["cvssV2"]["authentication"]
                            cvss_v2_userInteraction = "None"
                            cvss_v2_baseScore = cve_data["impact"]["baseMetricV2"]["cvssV2"]["baseScore"]
                        elif len(cvss_keys) == 0:
                            if "Rejected" in description:
                                # print(f"Rejected: {cve_id}")
                                cve_rejected += 1
                            elif "Rejected" not in description:
                            # print(f"No CVSS data for CVE: {cve_id} in file {nvd_path}")
                                # print(f"AWAITING ANALYSIS: {cve_id} - {nvd_path}")
                                cve_no_cvss += 1
                            else:
                                print("Unknown Status, Terminating")
                                sys.exit()
                        else:
                            print(cve_id)
                            print(nvd_file)
                            sys.exit()
                    except Exception as e:
                        print(e)
                    finally:
                        pass
                    
                    
                    # cvss_keys = cve_data["impact"].keys()
                    # if "baseMetricV3" in cvss_keys:
                    #     print(f"{cve_data["impact"]["baseMetricV3"]["cvssV3"]}\n")
                    # elif "baseMetricV2" in cvss_keys:
                    #     print(f"{cve_data["impact"]["baseMetricV2"]["cvssV2"]}\n")
                    # else:
                    #     print(f"{id}")
                    #     exit()
                        
                    #! print(f"{cve_data["cve"]["references"]["reference_data"]}\n")
                    # print(f"{cve_data["configurations"]}\n")
                    # print(f"{cve_data["publishedDate"]}\n")
                    # print(f"{cve_data["lastModifiedDate"]}\n")
                    
        
        except Exception as e:
            print(f"***** Error was: {e} *****")
        finally:
            pass
    
    print("")
    print(f"CVE Count: {cve_count}")
    print(f"CVEs with no CVSS: {cve_no_cvss}")
    print(f"Percentage of CVEs without CVSS {(cve_no_cvss/cve_count)}")
    print(f"Number of rejected CVEs: {cve_rejected}")
    
    
    
    impact_tuple = tuple(impact_list)
    print(f"Impact Tuple: \n{impact_tuple}")


def merge_nvd_data(nvd_data_files: list):
    master_cve_list = []

    
    for data_file in nvd_data_files:
        nvd_file_path = nvd_data_dir+data_file
        try:
            with open(nvd_file_path, encoding='utf-8') as nvd_file:
                nvd_data = nvd_file.read()
                nvd_json = json.loads(nvd_data)
        except Exception as e:
            print(f"File processing error: {e}")
        finally:
            # print(json.dumps(nvd_json["CVE_Items"], indent=4, sort_keys=True))
            nvd_cve_items = nvd_json["CVE_Items"]
            # print(type(nvd_cve_items))
            for nvd_cve in nvd_cve_items:
                master_cve_list.append(nvd_cve)
                # print(json.dumps(nvd_cve["cve"], indent=4, sort_keys=True))
                
    print(f"Number of CVE records: {len(master_cve_list)}")
    print(f"CVE list size in MB: {((sys.getsizeof(master_cve_list)/1024)/1024)}")
    # print(json.dumps(master_cve_list[0]["cve"], indent=4, sort_keys=True))
    
    cve_items_df = pd.DataFrame(master_cve_list)
    print(f"CVE DataFrame size in MB: {((sys.getsizeof(cve_items_df)/1024)/1024)}")
    
    try:
        nvd_master_file_path = nvd_data_dir+nvd_master_file
        cve_items_df.to_json(nvd_master_file_path)
    except Exception as e:
        print(f"Error writing nvd_master.json: {e}")
    finally:
        print(f"File {nvd_master_file} written to the filesystem")
    

def load_nvd_data(nvd_json_file: str = nvd_master_json_file) -> pd.DataFrame:
    df_nvd_data = pd.read_json(nvd_json_file)
    print(f"Loaded {nvd_json_file} with columns {df_nvd_data.columns}")
    return df_nvd_data


if __name__ == "__main__":
    app_config, _ =cve_config_bootstrap()
    process_nvd_files(app_config)
    
    # merge_nvd_data(["nvdcve-1.1-2002.json"])
    
    # merge_nvd_data(nvd_data_files)
    # df_nvd_data = load_nvd_data()
    # print(df_nvd_data.count())