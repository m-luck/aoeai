# automatically generated by the FlatBuffers compiler, do not modify

# namespace: AOC

import flatbuffers

class MapObject(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsMapObject(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = MapObject()
        x.Init(buf, n + offset)
        return x

    # MapObject
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # MapObject
    def Common(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            x = self._tab.Indirect(o + self._tab.Pos)
            from .CommonObjectInfo import CommonObjectInfo
            obj = CommonObjectInfo()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

def MapObjectStart(builder): builder.StartObject(1)
def MapObjectAddCommon(builder, common): builder.PrependUOffsetTRelativeSlot(0, flatbuffers.number_types.UOffsetTFlags.py_type(common), 0)
def MapObjectEnd(builder): return builder.EndObject()
