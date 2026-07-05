# mxCell Structure Reference

## mxfile Structure

```xml
<mxfile host="app.diagrams.net" generator="diagram-forge">
  <diagram id="..." name="Page-1">
    <mxGraphModel dx="..." dy="..." grid="1" gridSize="10">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- Nodes and edges here -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Required Elements

| Element | Description | Required |
|---------|-------------|----------|
| `mxCell id="0"` | Root cell | ✅ |
| `mxCell id="1" parent="0"` | Default parent | ✅ |
| Node mxCell | Has `vertex="1"` | ✅ |
| Edge mxCell | Has `edge="1"` | ✅ |

## Node Examples

### Rectangle

```xml
<mxCell id="node1" value="Node Name"
        style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
</mxCell>
```

### Ellipse (Start/End)

```xml
<mxCell id="start" value="Start"
        style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;"
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="80" height="50" as="geometry"/>
</mxCell>
```

### Diamond (Decision)

```xml
<mxCell id="decision1" value="Condition?"
        style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;"
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="100" height="80" as="geometry"/>
</mxCell>
```

## Edge Examples

### Arrow

```xml
<mxCell id="edge1" value=""
        style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
        edge="1" parent="1" source="node1" target="node2">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

### Labeled Edge

```xml
<mxCell id="edge2" value="Yes"
        style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
        edge="1" parent="1" source="decision1" target="node3">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

## Group (Container)

```xml
<!-- Container -->
<mxCell id="group1" value="Group Name"
        style="swimlane;horizontal=1;startSize=30;fillColor=#f5f5f5;strokeColor=#666666;"
        vertex="1" parent="1">
  <mxGeometry x="50" y="50" width="300" height="200" as="geometry"/>
</mxCell>

<!-- Child node (parent="group1") -->
<mxCell id="child1" value="Child Node"
        style="rounded=1;whiteSpace=wrap;html=1;"
        vertex="1" parent="group1">
  <mxGeometry x="20" y="40" width="100" height="50" as="geometry"/>
</mxCell>
```

## HTML Encoding

Content attribute requires HTML encoding:

| Character | Encoded |
|-----------|---------|
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&quot;` |
| `&` | `&amp;` |

## Validation Checklist

- [ ] `mxCell id="0"` and `id="1"` exist
- [ ] All nodes have `vertex="1"`
- [ ] All edges have `edge="1"`
- [ ] Edge `source`/`target` reference valid node IDs
- [ ] `mxGeometry` defined for each mxCell
- [ ] Content attribute properly HTML encoded
- [ ] mxCell count >= 2 + nodes + edges
