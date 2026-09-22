from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def load_yaml(relative_path):
    return yaml.safe_load((ROOT / relative_path).read_text())


def test_reference_registry_matches_hydra_folder_extraction_layout():
    config = load_yaml("config/config.yaml")
    registry = load_yaml("config/reference_files/reference_files_marvin.yaml")

    def registry_urls(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "url":
                    yield child
                else:
                    yield from registry_urls(child)

    assert all("/scratch/" not in url for url in registry_urls(registry))

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


def test_star_fusion_index_has_the_same_members_as_the_standalone_star_index():
    # Both folders are STAR indexes for hg19, so the star-fusion library must
    # carry every member file the standalone index has.  A member listed one
    # directory too high silently passes Hydra download and only fails the
    # package validation at the end of a build.
    registry = load_yaml("config/reference_files/reference_files_marvin.yaml")

    star_members = {
        member.split("/", 1)[1]
        for member in registry["star_reference"]["genome_dir"]["content_checksum"]
    }
    index_prefix = "ref_genome.fa.star.idx/"
    fusion_members = {
        member.split(index_prefix, 1)[1]
        for member in registry["star_fusion"]["content_checksum"]
        if index_prefix in member
    }

    assert not star_members - fusion_members


def test_reference_registries_agree_on_checksums():
    marvin = load_yaml("config/reference_files/reference_files_marvin.yaml")
    miarka = load_yaml("config/reference_files/reference_files_miarka.yaml")

    def checksums(value, prefix=""):
        if not isinstance(value, dict):
            return
        for key, child in value.items():
            name = f"{prefix}.{key}" if prefix else key
            if key in ("checksum", "compressed_checksum"):
                yield name, child
            elif key == "content_checksum":
                for member, digest in child.items():
                    yield f"{name}.{member}", digest
            else:
                yield from checksums(child, name)

    assert dict(checksums(marvin)) == dict(checksums(miarka))
