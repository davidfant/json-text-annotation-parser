from dataclasses import dataclass
from typing import Any, Callable, List, Literal, Dict, Tuple, Set
import json


@dataclass
class JSONTraverser:
  @dataclass
  class Node:
    id: str
    path: List[str | int]
    value: Any

  @dataclass
  class Event(Node):
    offset: int
    type: Literal['start', 'end']

  indent: int = 2
  callback: Callable[[Event], None] = lambda event: None

  def traverse(
    self,
    data: Any,
    path: List[str | int] = [],
    offset: int = 0,
  ) -> Tuple[str, int]:
    node_id = path_to_id(path)
    self.callback(JSONTraverser.Event(node_id, path, data, offset, 'start'))

    dumped: str
    if isinstance(data, dict):
      dumped = self.traverse_dict(data, path, offset)
    elif isinstance(data, list):
      dumped = self.traverse_list(data, path, offset)
    elif isinstance(data, (str, int, float, bool)) or data is None:
      dumped = self.traverse_primitive(data)
    else:
      raise TypeError(f"Type {type(data)} is not JSON serializable")

    offset += len(dumped)
    self.callback(JSONTraverser.Event(node_id, path, data, offset, 'end'))
    return dumped, offset

  def traverse_dict(self, data: Dict, path: List[str | int], offset: int):
    indent_current = ' ' * self.indent * len(path)
    indent_next = ' ' * self.indent * (len(path) + 1)

    dict_prefix = '{\n'
    dict_suffix = '\n' + indent_current + '}'

    offset += len(dict_prefix)

    dict_strs = []
    key_suffix = ',\n'
    for key, value in data.items():
      key_prefix = f'{indent_next}{json.dumps(key)}: '
      offset += len(key_prefix)
      val_str, offset = self.traverse(value, path + [key], offset)
      dict_strs.append(f'{key_prefix}{val_str}')
      offset += len(key_suffix)
    offset -= len(key_suffix)
    offset += len(dict_suffix)

    dict_str = key_suffix.join(dict_strs)

    return f'{dict_prefix}{dict_str}{dict_suffix}'

  def traverse_list(self, data: List, path: List[str | int], offset: int):
    indent_current = ' ' * self.indent * len(path)
    indent_next = ' ' * self.indent * (len(path) + 1)

    list_prefix = '[\n'
    list_suffix = '\n' + indent_current + ']'

    offset += len(list_prefix)

    list_strs = []
    item_prefix = indent_next
    item_suffix = ',\n'
    for index, item in enumerate(data):
      offset += len(item_prefix)
      val_str, offset = self.traverse(item, path + [index], offset)
      list_strs.append(f'{item_prefix}{val_str}')
      offset += len(item_suffix)
    offset -= len(item_suffix)
    offset += len(list_suffix)

    list_str = item_suffix.join(list_strs)

    return f'{list_prefix}{list_str}{list_suffix}'


  def traverse_primitive(self, data: str | int | float | bool | None):
    return json.dumps(data)



def path_to_id(path: List[str | int]) -> str:
  id = '$'
  for p in path:
    if isinstance(p, int):
      id += f'[{p}]'
    else:
      id += f'.{p}'
  return id

