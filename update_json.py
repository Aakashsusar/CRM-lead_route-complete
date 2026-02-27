import json

file_path = "apps/crm/crm/lead_syncing/doctype/lead_sync_source/lead_sync_source.json"
with open(file_path, 'r') as f:
    data = json.load(f)

for field in data.get("fields", []):
    if field.get("fieldname") == "background_sync_frequency":
        options = field.get("options", "").split("\n")
        if "Every 2 Minutes" not in options:
            options.insert(0, "Every 2 Minutes")
            field["options"] = "\n".join(options)
        break

with open(file_path, 'w') as f:
    json.dump(data, f, indent=1)
