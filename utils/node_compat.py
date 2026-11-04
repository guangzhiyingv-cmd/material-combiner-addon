"""Blender node lookup helpers compatible with localized interfaces."""

from typing import Iterable, Optional


def _normalize(value: object) -> str:
    """Normalize labels so English and localized names can be compared."""
    if value is None:
        return ""

    return "".join(
        character
        for character in str(value).casefold()
        if character.isalnum()
    )


NODE_TYPE_ALIASES = {
    "materialoutput": "ShaderNodeOutputMaterial",
    "principledbsdf": "ShaderNodeBsdfPrincipled",
    "diffusebsdf": "ShaderNodeBsdfDiffuse",
    "specularbsdf": "ShaderNodeEeveeSpecular",
    "emission": "ShaderNodeEmission",
    "imagetexture": "ShaderNodeTexImage",
    "normalmap": "ShaderNodeNormalMap",
    "rgb": "ShaderNodeRGB",
    "group": "ShaderNodeGroup",
}

NODE_NAME_ALIASES = {
    "principledbsdf": (
        "Principled BSDF",
        "原理化BSDF",
        "原理化 Bsdf",
        "原理化着色器",
    ),
    "imagetexture": (
        "Image Texture",
        "图像纹理",
        "图片纹理",
    ),
    "diffusebsdf": (
        "Diffuse BSDF",
        "漫射BSDF",
        "漫射 Bsdf",
    ),
    "specularbsdf": (
        "Specular BSDF",
        "高光BSDF",
        "镜面BSDF",
    ),
    "emission": (
        "Emission",
        "自发光",
    ),
    "normalmap": (
        "Normal Map",
        "法线贴图",
    ),
    "materialoutput": (
        "Material Output",
        "材质输出",
    ),
    "group": (
        "Group",
        "组",
        "节点组",
    ),
}

NODE_FRAGMENT_ALIASES = {
    "mmdshader": ("mmdshader", "mmd材质", "mmd着色器"),
    "mmdbasetex": ("mmdbasetex", "mmd基础纹理", "mmd基础贴图"),
    "mtoon1materialmtoon1output": (
        "mtoon1materialmtoon1output",
        "mtoon1输出",
    ),
    "mtoon1basecolortextureimage": (
        "mtoon1basecolortextureimage",
        "mtoon1基础色纹理",
        "mtoon1基础色贴图",
    ),
    "mtoon1pbrmetallicroughnessbasecolorfactor": (
        "mtoon1pbrmetallicroughnessbasecolorfactor",
        "基础色因子",
        "基础颜色因子",
    ),
}

SOCKET_ALIASES = {
    "basecolor": ("Base Color", "基础色", "基础颜色"),
    "color": ("Color", "颜色"),
    "diffusecolor": ("Diffuse Color", "漫射颜色"),
    "diffuse": ("Diffuse", "漫射"),
    "alpha": ("Alpha", "透明度"),
    "metallic": ("Metallic", "金属度", "金属性"),
    "roughness": ("Roughness", "粗糙度"),
    "speculartint": ("Specular Tint", "高光色调", "镜面色调"),
    "specular": ("Specular", "高光", "镜面"),
    "emissioncolor": (
        "Emission Color",
        "自发光颜色",
        "发光颜色",
    ),
    "emissivecolor": (
        "Emissive Color",
        "自发光颜色",
        "发光颜色",
    ),
    "emissionstrength": (
        "Emission Strength",
        "自发光强度",
        "发光强度",
    ),
    "normal": ("Normal", "法线"),
}


def _alias_values(name: str) -> Iterable[str]:
    normalized = _normalize(name)
    yield name
    yield from NODE_NAME_ALIASES.get(normalized, ())
    yield from NODE_FRAGMENT_ALIASES.get(normalized, ())


def find_node(nodes, name: str):
    """Find a node by English name, type identifier, or localized alias."""
    if nodes is None:
        return None

    try:
        node = nodes.get(name)
    except (AttributeError, KeyError, TypeError):
        node = None
    if node is not None:
        return node

    normalized = _normalize(name)
    type_name = NODE_TYPE_ALIASES.get(normalized)
    if type_name:
        for candidate in nodes:
            if getattr(candidate, "bl_idname", "") == type_name:
                return candidate

    aliases = {_normalize(alias) for alias in _alias_values(name)}
    for candidate in nodes:
        values = (
            getattr(candidate, "name", ""),
            getattr(candidate, "label", ""),
            getattr(candidate, "bl_idname", ""),
        )
        normalized_values = {_normalize(value) for value in values}
        if aliases & normalized_values:
            return candidate

        for alias in aliases:
            if alias and any(alias in value for value in normalized_values):
                return candidate

    return None


def node_exists(nodes, name: str) -> bool:
    """Return whether a compatible node exists."""
    return find_node(nodes, name) is not None


def _find_socket(collection, name: str):
    if collection is None:
        return None

    try:
        socket = collection.get(name)
    except (AttributeError, KeyError, TypeError):
        socket = None
    if socket is not None:
        return socket

    normalized = _normalize(name)
    aliases = {
        _normalize(alias)
        for alias in SOCKET_ALIASES.get(normalized, (name,))
    }

    for socket in collection:
        values = {
            _normalize(getattr(socket, "name", "")),
            _normalize(getattr(socket, "identifier", "")),
        }
        if aliases & values:
            return socket

    return None


def get_input(node, name: str):
    """Find an input socket by stable identifier or localized alias."""
    if node is None or not hasattr(node, "inputs"):
        return None
    return _find_socket(node.inputs, name)


def get_output(node, name: str):
    """Find an output socket by stable identifier or localized alias."""
    if node is None or not hasattr(node, "outputs"):
        return None
    return _find_socket(node.outputs, name)


def matches_socket_name(value: object, terms: Iterable[str]) -> bool:
    """Check a socket label against English and localized search terms."""
    normalized_value = _normalize(value)
    return any(
        _normalize(term) in normalized_value
        for term in terms
        if term
    )
