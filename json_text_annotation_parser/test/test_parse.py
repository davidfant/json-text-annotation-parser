import json
import unittest
from typing import Any, List, Tuple
from ..parse import parse, TextAnnotation

start_char = '🟢'
end_char = '🔴'

def prepare(value: Any) -> Tuple[Any, List[TextAnnotation]]:
  annotations = []
  offset = 0
  special_chars = 0
  while offset < len(value):
    start = value.find(start_char, offset)
    if start == -1: break
    start -= special_chars
    special_chars += 1

    end = value.find(end_char, offset)
    if end == -1: break
    end -= special_chars
    special_chars += 1

    annotations.append(TextAnnotation(start, end))
    offset = end + special_chars
  

  value = value.replace(start_char, '')
  value = value.replace(end_char, '')

  return json.loads(value), annotations

class JSONTextAnnotationParserTest(unittest.TestCase):

  def test_parse_string_content(self):
    value, annotations = prepare('''
{
  "key": "🟢value🔴"
}
    '''.strip())
    parsed = parse(value, annotations)
    self.assertEqual(parsed, [['key']])


  def test_parse_full_line_incl_ending_comma(self):
    value, annotations = prepare('''
{
  🟢"first": "1",🔴
  "second": "2"
}
    '''.strip())
    parsed = parse(value, annotations)
    self.assertEqual(parsed, [['first']])
  

  def test_parse_partial_object(self):
    value, annotations = prepare('''
{
  🟢"first": "1",
  "second": "2"🔴,
  "third": "3"
}
    '''.strip())
    parsed = parse(value, annotations)
    self.assertEqual(parsed, [['first'], ['second']])  


  def test_parse_partial_list(self):
    value, annotations = prepare('''
{
  "list": [
    0,
    🟢1,
    2,🔴
    3
  ]
}
    '''.strip())
    parsed = parse(value, annotations)
    self.assertEqual(parsed, [['list', 1], ['list', 2]])


  def test_multiple_annotations(self):
    value, annotations = prepare('''
{
  "list": [
    0,
    🟢1,
    2,🔴
    3,
    🟢4,🔴
    5
  ],
  "key": "🟢value",
  "key2": "value2"🔴
}
    '''.strip())
    parsed = parse(value, annotations)
    self.assertEqual(parsed, [
      ['list', 1],
      ['list', 2],
      ['list', 4],
      ['key'],
      ['key2'],
    ])


  def test_nested_objects(self):
    value, annotations = prepare('''
{
  "0": {
    "1": 🟢{
      "2": {
        "3": {
          "a": true,
          "b": false
        },
        "c": true,🔴
        "d": false
      }
    }
  }
}
    '''.strip())
    parsed = parse(value, annotations)
    self.assertEqual(parsed, [
      ['0', '1', '2', '3'],
      ['0', '1', '2', 'c'],
    ])
  



if __name__ == '__main__':
  unittest.main()
