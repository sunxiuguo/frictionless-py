from frictionless import Resource

# General


def test_resource_infer():
    resource = Resource(path="data/table.csv")
    resource.infer(stats=True)
    assert resource.to_descriptor() == {
        "name": "table",
        "path": "data/table.csv",
        "type": "table",
        "scheme": "file",
        "format": "csv",
        "encoding": "utf-8",
        "mediatype": "text/csv",
        "hash": "sha256:a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8",
        "bytes": 30,
        "fields": 2,
        "rows": 2,
        "schema": {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ]
        },
    }


def test_resource_infer_source_non_tabular():
    resource = Resource(path="data/text.txt")
    resource.infer(stats=True)
    assert resource.to_descriptor() == {
        "name": "text",
        "type": "text",
        "path": "data/text.txt",
        "scheme": "file",
        "format": "txt",
        "encoding": "utf-8",
        "mediatype": "text/txt",
        "hash": "sha256:b9e68e1bea3e5b19ca6b2f98b73a54b73daafaa250484902e09982e07a12e733",
        "bytes": 5,
    }


def test_resource_infer_from_path():
    resource = Resource("data/table.csv")
    resource.infer(stats=True)
    assert resource.path == "data/table.csv"


def test_resource_infer_basepath_with_forward_slash_drive(tmp_path, monkeypatch):
    basepath = tmp_path.as_posix()
    if not tmp_path.drive:
        # Exercise drive-path routing on POSIX using a synthetic local directory.
        monkeypatch.chdir(tmp_path)
        basepath = "C:/data"
        (tmp_path / basepath).mkdir(parents=True)
    (tmp_path / basepath / "table.csv").write_text("x,y\n1,2\n", encoding="utf-8")

    resource = Resource(path="table.csv", basepath=basepath)
    resource.infer(stats=True)

    assert resource.scheme == "file"
    assert resource.schema.to_descriptor() == {
        "fields": [{"name": "x", "type": "integer"}, {"name": "y", "type": "integer"}]
    }
    assert resource.stats.rows == 1
    assert resource.read_rows() == [{"x": 1, "y": 2}]


# Bugs


def test_resource_infer_not_slugified_name_issue_531():
    resource = Resource("data/Table With Data.csv")
    resource.infer(stats=True)
    assert resource.name == "table-with-data"
