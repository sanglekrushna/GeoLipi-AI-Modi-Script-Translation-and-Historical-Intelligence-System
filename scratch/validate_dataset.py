import json
import os

def validate_dataset(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Total sites: {len(data)}")
        
        all_have_image = True
        broken_images = []
        for i, site in enumerate(data):
            if "image" not in site or not site["image"]:
                all_have_image = False
                print(f"Site {i+1} ({site.get('name', 'Unknown')}) missing image field.")
            elif not site["image"].startswith("http"):
                broken_images.append(site["name"])
        
        print(f"All 30 sites contain 'image': {all_have_image and len(data) == 30}")
        print(f"Non-empty image fields: {all(site.get('image') for site in data)}")
        print(f"Broken/non-http image links: {broken_images if broken_images else 'None'}")
        
        # Check for duplicate images
        images = [site["image"] for site in data if "image" in site]
        duplicates = set([x for x in images if images.count(x) > 1])
        print(f"Duplicate images: {duplicates if duplicates else 'None'}")
        
        return len(data) == 30 and all_have_image and not broken_images
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    validate_dataset(r"d:\ACADEMICS\SY\Semester 4th\ML\COURSE PROJECT\modi_locations.json")
