# import boto3
import data
import pickle

# import secrets


class Configuration:
    def __init__(
        self,
        token,
        target_id,
        group_ids,
        group_descriptions,
        group_titles,
        group_snumbers,
    ):
        self.token = token
        self.target_id = target_id
        self.group_ids = group_ids
        self.group_descriptions = group_descriptions
        self.group_titles = group_titles
        self.group_snumbers = group_snumbers

    def __str__(self):
        return f"TOK: {self.token}\nTARGET_ID: {self.target_id}\nGROUP_IDS: {self.group_ids}\nGROUP_DESCRIPTIONS: {self.group_descriptions}\n"


def parse_entries(config_name, entries):
    isinside = False
    result = []
    for entry in entries:
        if entry == config_name:
            isinside = True
            continue
        if isinside and entry == "END":
            break
        if isinside:
            result.append(entry[1:])
    return result


def parse_config(filename):
    file = open(filename, "r")
    entries = file.read().splitlines()
    file.close()

    token = parse_entries("TOKEN", entries)
    target_id = parse_entries("TARGET_ID", entries)
    group_ids = parse_entries("GROUP_IDS", entries)
    group_descriptions = parse_entries("GROUP_DESCRIPTIONS", entries)
    group_titles = [
        group_description.split(":")[0] for group_description in group_descriptions
    ]
    group_snumbers = [
        group_description.split(":")[1] for group_description in group_descriptions
    ]

    return Configuration(
        token, target_id, group_ids, group_descriptions, group_titles, group_snumbers
    )


def save():
    with open("data.pkl", "wb") as file:
        pickle.dump(
            [
                data.master_group_titles_with_photo_ids,
                data.master_photo_unique_ids,
                data.group_titles_with_photo_ids,
                data.group_titles_with_photo_unique_ids,
                data.group_titles_with_duplicate_photo_unique_id_count,
            ],
            file,
            protocol=pickle.HIGHEST_PROTOCOL,
        )


# def save():
#     client = boto3.client("s3", aws_access_key_id=secrets.access_key,
#                           aws_secret_access_key=secrets.secret_access_key)
#     bucket_name = "inscreen-bucket"
#     object_name = "data.pkl"
#     file_path = "/tmp/"
#     file_name = "data.pkl"

#     with open(file_path + file_name, "wb") as file:
#         pickle.dump([data.master_group_titles_with_photo_ids, data.master_photo_unique_ids, data.group_titles_with_photo_ids,
#                      data.group_titles_with_photo_unique_ids, data.group_titles_with_duplicate_photo_unique_id_count], file, protocol=pickle.HIGHEST_PROTOCOL)

#     with open(file_path + file_name, "rb") as file:
#         client.upload_fileobj(file, bucket_name, object_name)


def load():
    with open("data.pkl", "rb") as file:
        (
            data.master_group_titles_with_photo_ids,
            data.master_photo_unique_ids,
            data.group_titles_with_photo_ids,
            data.group_titles_with_photo_unique_ids,
            data.group_titles_with_duplicate_photo_unique_id_count,
        ) = pickle.load(file)


# def load():
#     client = boto3.client("s3", aws_access_key_id=secrets.access_key,
#                           aws_secret_access_key=secrets.secret_access_key)
#     bucket_name = "inscreen-bucket"
#     object_name = "data.pkl"
#     file_path = "/tmp/"
#     file_name = "data.pkl"

#     with open(file_path + file_name, "wb") as file:
#         client.download_fileobj(bucket_name, object_name, file)

#     with open(file_path + file_name, "rb") as file:
#         data.master_group_titles_with_photo_ids, data.master_photo_unique_ids, data.group_titles_with_photo_ids, data.group_titles_with_photo_unique_ids, data.group_titles_with_duplicate_photo_unique_id_count = pickle.load(
#             file)
