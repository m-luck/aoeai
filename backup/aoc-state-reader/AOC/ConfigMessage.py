# automatically generated by the FlatBuffers compiler, do not modify

# namespace: AOC

import flatbuffers

class ConfigMessage(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsConfigMessage(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = ConfigMessage()
        x.Init(buf, n + offset)
        return x

    # ConfigMessage
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # ConfigMessage
    def TickInterval(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint32Flags, o + self._tab.Pos)
        return 500

    # ConfigMessage
    def MapObjectTickInterval(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint32Flags, o + self._tab.Pos)
        return 15000

    # ConfigMessage
    def UpdateCycles(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int32Flags, o + self._tab.Pos)
        return 1

    # ConfigMessage
    def PlayerRestriction(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int8Flags, o + self._tab.Pos)
        return 0

    # ConfigMessage
    def PlayerRestrictV(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(flatbuffers.number_types.Int8Flags, a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 1))
        return 0

    # ConfigMessage
    def PlayerRestrictVAsNumpy(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            return self._tab.GetVectorAsNumpy(flatbuffers.number_types.Int8Flags, o)
        return 0

    # ConfigMessage
    def PlayerRestrictVLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # ConfigMessage
    def ObjectRestriction(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(14))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int8Flags, o + self._tab.Pos)
        return 0

    # ConfigMessage
    def ObjectRestrictV(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(16))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(flatbuffers.number_types.Uint32Flags, a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 4))
        return 0

    # ConfigMessage
    def ObjectRestrictVAsNumpy(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(16))
        if o != 0:
            return self._tab.GetVectorAsNumpy(flatbuffers.number_types.Uint32Flags, o)
        return 0

    # ConfigMessage
    def ObjectRestrictVLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(16))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

def ConfigMessageStart(builder): builder.StartObject(7)
def ConfigMessageAddTickInterval(builder, tickInterval): builder.PrependUint32Slot(0, tickInterval, 500)
def ConfigMessageAddMapObjectTickInterval(builder, mapObjectTickInterval): builder.PrependUint32Slot(1, mapObjectTickInterval, 15000)
def ConfigMessageAddUpdateCycles(builder, updateCycles): builder.PrependInt32Slot(2, updateCycles, 1)
def ConfigMessageAddPlayerRestriction(builder, playerRestriction): builder.PrependInt8Slot(3, playerRestriction, 0)
def ConfigMessageAddPlayerRestrictV(builder, playerRestrictV): builder.PrependUOffsetTRelativeSlot(4, flatbuffers.number_types.UOffsetTFlags.py_type(playerRestrictV), 0)
def ConfigMessageStartPlayerRestrictVVector(builder, numElems): return builder.StartVector(1, numElems, 1)
def ConfigMessageAddObjectRestriction(builder, objectRestriction): builder.PrependInt8Slot(5, objectRestriction, 0)
def ConfigMessageAddObjectRestrictV(builder, objectRestrictV): builder.PrependUOffsetTRelativeSlot(6, flatbuffers.number_types.UOffsetTFlags.py_type(objectRestrictV), 0)
def ConfigMessageStartObjectRestrictVVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def ConfigMessageEnd(builder): return builder.EndObject()
