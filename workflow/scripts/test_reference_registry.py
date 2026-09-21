from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def load_yaml(relative_path):
    return yaml.safe_load((ROOT / relative_path).read_text())


def test_reference_registry_matches_hydra_folder_extraction_layout():
    config = load_yaml("config/config.yaml")
    registry = load_yaml("config/reference_files/reference_files_marvin.yaml")

    genome_size = registry["reference"]["genomesize_xml"]
    assert genome_size["path"] == "pickett/GenomeSize.xml"
    assert genome_size["checksum"] == "75adc2022af4deaabd7444d9d1d02c88"

    star = registry["star_reference"]["genome_dir"]
    star_root = next(iter(star["content_checksum"])).split("/", 1)[0]
    star_destination = Path(star["path"]).relative_to("pickett")
    expected_star = f"{{{{REFERENCE_DATA}}}}/{star_destination}/{star_root}/"
    assert config["star"]["genome_index"] == expected_star

    star_fusion = registry["star_fusion"]
    first_member = next(iter(star_fusion["content_checksum"]))
    fusion_library = first_member.split("/ctat_genome_lib_build_dir/", 1)[0]
    fusion_destination = Path(star_fusion["path"]).relative_to("pickett")
    expected_fusion = (
        f"{{{{REFERENCE_DATA}}}}/{fusion_destination}/{fusion_library}/"
        "ctat_genome_lib_build_dir/"
    )
    assert config["star_fusion"]["genome_path"] == expected_fusion

    folder_entries = [
        star,
        registry["fusioncatcher_files"],
        star_fusion,
    ]
    assert all(not entry["path"].endswith(".tar.gz") for entry in folder_entries)
