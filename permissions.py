import yaml


class User:
    def __init__(self, username):
        self.username = username
        self.permissions = []

    def add_permissions_from_tree(self, tree_data, paths_to_add):
        for path_name in generate_full_path_names(tree_data):
            if path_name in paths_to_add:
                permission = Permission(path_name)
                self.permissions.append(permission)

    def save_to_yaml(self, filename):
        with open(filename, 'r') as f:
            data = yaml.safe_load(f)

        if 'credentials' in data and 'usernames' in data['credentials'] and self.username in data['credentials'][
            'usernames']:
            data['credentials']['usernames'][self.username]['permissions'] = [permission.name for permission in
                                                                              self.permissions]

        with open(filename, 'w') as f:
            yaml.dump(data, f)

    def load_from_yaml(self, filename):
        with open(filename, 'r') as f:
            data = yaml.safe_load(f)

        if 'credentials' in data and 'usernames' in data['credentials'] and self.username in data['credentials'][
            'usernames']:
            self.permissions = [Permission(name) for name in
                                data['credentials']['usernames'][self.username].get('permissions', [])]


class Permission:
    def __init__(self, name):
        self.name = name


def generate_full_path_names(data, path=None):
    path = path or []
    for item in data:
        new_path = path + [item['name']]
        yield '/'.join(new_path)
        if 'children' in item:
            yield from generate_full_path_names(item['children'], new_path)


data_origin = [
    {
        "name": "root1",
        "children": [
            {
                "name": "child1",
                "children": [
                    {
                        "name": "grandchild1",
                        "children": []
                    },
                    {
                        "name": "grandchild2",
                        "children": []
                    }
                ]
            },
            {
                "name": "child2",
                "children": []
            }
        ]
    },
    {
        "name": "root2",
        "children": [
            {
                "name": "child1",
                "children": []
            }
        ]
    },
    {
        "name": "root3"
    }
]

# 添加权限并保存到YAML文件
user = User('jsmith')
# paths_to_add = ['root1/child1/grandchild1', 'root2/child1']
# user.add_permissions_from_tree(data_origin, paths_to_add)
# user.save_to_yaml('config.yaml')

# 从YAML文件加载权限
user.load_from_yaml('config.yaml')
print([permission.name for permission in user.permissions])  # 输出：['root1/child1/grandchild1', 'root2/child1']
