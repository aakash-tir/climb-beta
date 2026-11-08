import xml.etree.ElementTree as ET
from pathlib import Path

from scripts import ROOT, load_script

from climb_beta.config import load_classes, load_colour_config, parse_colour_config
from climb_beta.labelling import schema
from climb_beta.labelling.make_config import build_config


def _parse(xml: str) -> ET.Element:
    return ET.fromstring(xml.split("-->", 1)[1])


def test_config_has_every_class_colour_and_per_region_choices() -> None:
    cfg = load_colour_config()
    root = _parse(build_config(load_classes(), cfg))
    by_name = {el.get("name"): el for el in root.iter() if el.get("name")}
    for tag in (schema.BRUSH, schema.POLYGON, schema.KEYPOINT, schema.RECT):
        assert [lb.get("value") for lb in by_name[tag]] == ["hold", "volume", "tape"]
    assert by_name[schema.KEYPOINT].get("smart") == "true"
    colour = by_name[schema.COLOUR]
    assert colour.get("perRegion") == "true"
    assert [c.get("value") for c in colour] == list(cfg.names)
    assert by_name[schema.CHALKED].get("perRegion") == "true"
    assert all(el.get("toName") == schema.IMAGE for el in by_name.values() if el.get("toName"))


def test_editing_colours_yaml_changes_choices() -> None:
    cfg = parse_colour_config(
        {
            "colours": [
                {"name": "red", "family": "redpink"},
                {"name": "pink", "family": "redpink"},
                {"name": "teal", "family": "blue", "swatch": "#008080"},
            ],
            "families": {"redpink": {"hue": [[0, 9]]}, "blue": {"hue": [[86, 128]]}},
            "thresholds": {},
        }
    )
    root = _parse(build_config(("hold",), cfg))
    colour = next(el for el in root.iter("Choices") if el.get("name") == schema.COLOUR)
    assert [c.get("value") for c in colour] == ["red", "pink", "teal"]


def test_committed_xml_is_up_to_date() -> None:
    mod = load_script("labelling/make_config.py")
    assert mod.main(["--check"]) == 0, "run: python labelling/make_config.py"


def test_check_detects_stale(tmp_path: Path) -> None:
    mod = load_script("labelling/make_config.py")
    stale = tmp_path / "x.xml"
    stale.write_text("<View/>")
    assert mod.main(["--check", "--out", str(stale)]) == 1
    assert mod.main(["--out", str(stale)]) == 0
    assert mod.main(["--check", "--out", str(stale)]) == 0
    assert (ROOT / "labelling" / "label_config.xml").exists()
