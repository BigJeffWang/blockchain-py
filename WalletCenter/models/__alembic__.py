import importlib
import os
from alembic.script.revision import Revision
import alembic


class RevisionDiy(Revision):
    def __init__(self, revision, down_revision, **kwargs):
        revision = revision + "wangye"
        super().__init__(revision, down_revision, **kwargs)


class Script(alembic.script.base.Script):
    def __init__(self, module, rev_id, path):
        super().__init__(module, rev_id, path)


def dynamic_import_model(class_file, class_name, import_path="models"):
    print(import_path + '.%s' % class_file[:-3])
    tmp_model = importlib.import_module(import_path + '.%s' % class_file[:-3])
    globals()[class_name] = getattr(tmp_model, class_name)


def get_class_name(model_file):
    return "".join([x.capitalize() for x in model_file.split("_")])[:-3]


def get_sub_model_path_list(model_path):
    sub_model_path_list = []
    for root, dirs, _ in os.walk(model_path):
        for dir in dirs:
            if dir[:2] != "__":
                sub_model_path = os.path.join(root, dir)
                sub_model_path_list.append(sub_model_path)
    return sub_model_path_list


def call_dynamic():
    dir_name = os.path.dirname(__file__)[os.path.dirname(__file__).rfind(os.sep) + 1:]
    exclude_files = ['base_model.py']
    model_path = os.sep.join([os.path.dirname(os.path.dirname(os.path.realpath(__file__))), dir_name])
    model_path_list = [model_path] + get_sub_model_path_list(model_path)
    for model_path in model_path_list:
        import_path = model_path[model_path.rfind(dir_name):].replace(os.sep, ".")
        m_list = [m for m in os.listdir(model_path) if m[-3:] == ".py"]
        model_files = [mf for mf in m_list if mf[:2] != "__" and mf not in exclude_files]
        for i in model_files:
            try:
                dynamic_import_model(i, get_class_name(i), import_path)
            except Exception as e:
                print("import model error: ", e)


if __name__ == "__main__":
    call_dynamic()
