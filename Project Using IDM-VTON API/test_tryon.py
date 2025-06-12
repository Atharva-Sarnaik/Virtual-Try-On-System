import os
import replicate

# Set your API token
os.environ["REPLICATE_API_TOKEN"] = "r8_OQjJZBH7dbuA3PyvwSncjey7GJAAV4w3NvZE3"

output = replicate.run(
    "cuuupid/idm-vton:0513734a452173b8173e907e3a59d19a36266e55b48528559432bd21c7d7e985",
    input={
        "crop": False,
        "seed": 42,
        "steps": 30,
        "category": "upper_body",
        "force_dc": False,
        "garm_img": "https://replicate.delivery/pbxt/KgwTlZyFx5aUU3gc5gMiKuD5nNPTgliMlLUWx160G4z99YjO/sweater.webp",
        "human_img": "https://replicate.delivery/pbxt/KgwTlhCMvDagRrcVzZJbuozNJ8esPqiNAIJS3eMgHrYuHmW4/KakaoTalk_Photo_2024-04-04-21-44-45.png",
        "mask_only": False,
        "garment_des": "cute pink top"
    }
)
print(output) 