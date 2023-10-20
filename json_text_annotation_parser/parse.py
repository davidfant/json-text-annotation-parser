import json
from dataclasses import dataclass
from typing import Any, Callable, List, Literal, Dict, Tuple, Set
from .traverser import JSONTraverser, path_to_id

@dataclass
class TextAnnotation:
  start: int
  end: int


def parse(value: Any, annotations: List[TextAnnotation]) -> List[List[str | int]]:
  events: List[JSONTraverser.Event] = []
  traverser = JSONTraverser(callback=events.append)
  traverser.traverse(value)

  node_by_id: Dict[str, JSONTraverser.Node] = {}
  node_range: Dict[str, Tuple[int, int]] = {}

  for event in events:
    node_by_id[event.id] = event
    if event.type == 'start':
      node_range[event.id] = (event.offset, 0)
    elif event.type == 'end':
      node_range[event.id] = (node_range[event.id][0], event.offset)
  
  # assuming annotations don't overlap
  return [
    path 
    for annotation in annotations
    for path in parse_annotation(annotation, node_by_id, node_range)
  ]
  

def parse_annotation(
  annotation: TextAnnotation,
  node_by_id: Dict[str, JSONTraverser.Node],
  node_range: Dict[str, Tuple[int, int]],
) -> List[List[str | int]]:
  intersecting_node_ids: List[str] = []
  for node_id, (node_start, node_end) in node_range.items():
    # if node intersects with annotation
    if (
      annotation.start <= node_end and
      annotation.end >= node_start
    ):
      intersecting_node_ids.append(node_id)
  
  most_specific_node_id: str | int | None = None
  most_specific_node_intersecting_child_ids: List[str] = []

  # Assumes intersecting_node_ids is sorted from parent -> child
  for node_id in intersecting_node_ids:
    node = node_by_id[node_id]

    node_child_ids = [
      id
      for id, child in node_by_id.items()
      if (
        len(child.path) == len(node.path) + 1 and
        child.path[:len(node.path)] == node.path
      )
    ]

    intersecting_child_ids = [
      id
      for id in node_child_ids
      if id in intersecting_node_ids
    ]

    if (
      not most_specific_node_id or
      len(node.path) > len(node_by_id[most_specific_node_id].path)
    ):
      most_specific_node_id = node_id
      most_specific_node_intersecting_child_ids = intersecting_child_ids

      has_multiple_intersecting_children = len(intersecting_child_ids) > 1
      all_children_are_intersecting = len(intersecting_child_ids) == len(node_child_ids)
      if has_multiple_intersecting_children and not all_children_are_intersecting:
        break

  if not most_specific_node_id:
    return []
  
  most_specific_node = node_by_id[most_specific_node_id]
  if most_specific_node_intersecting_child_ids:
    child_path_last_value = [
      node_by_id[id].path[-1]
      for id in most_specific_node_intersecting_child_ids
    ]
    if len(child_path_last_value) == 1:
      return [
        most_specific_node.path + [child_path_last_value[0]]
      ]

    return [
      most_specific_node.path + [child_path_last_value]
      for child_path_last_value in child_path_last_value
    ]
  elif not isinstance(most_specific_node.value, (dict, list)):
    return [most_specific_node.path]
  else:
    return []

