# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: agent.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='agent.proto',
  package='gaiachain',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=b'\n\x0b\x61gent.proto\x12\tgaiachain\"\xda\x01\n\x05\x41gent\x12\x12\n\npublic_key\x18\x01 \x01(\t\x12\r\n\x05\x65mail\x18\x02 \x01(\t\x12\x14\n\x0c\x63ompany_name\x18\x03 \x01(\t\x12#\n\x04role\x18\x04 \x01(\x0e\x32\x15.gaiachain.Agent.Role\x12\x11\n\ttimestamp\x18\x05 \x01(\x04\"`\n\x04Role\x12\x0e\n\nSUPER_USER\x10\x00\x12\r\n\tINSPECTOR\x10\x01\x12\x07\n\x03PCA\x10\x02\x12\x10\n\x0cWAREHOUSEMAN\x10\x03\x12\x1e\n\x1a\x43OOPERATIVE_REPRESENTATIVE\x10\x04\"3\n\x0e\x41gentContainer\x12!\n\x07\x65ntries\x18\x01 \x03(\x0b\x32\x10.gaiachain.Agentb\x06proto3'
)



_AGENT_ROLE = _descriptor.EnumDescriptor(
  name='Role',
  full_name='gaiachain.Agent.Role',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='SUPER_USER', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='INSPECTOR', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PCA', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='WAREHOUSEMAN', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='COOPERATIVE_REPRESENTATIVE', index=4, number=4,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=149,
  serialized_end=245,
)
_sym_db.RegisterEnumDescriptor(_AGENT_ROLE)


_AGENT = _descriptor.Descriptor(
  name='Agent',
  full_name='gaiachain.Agent',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='public_key', full_name='gaiachain.Agent.public_key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='email', full_name='gaiachain.Agent.email', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='company_name', full_name='gaiachain.Agent.company_name', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='role', full_name='gaiachain.Agent.role', index=3,
      number=4, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='gaiachain.Agent.timestamp', index=4,
      number=5, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _AGENT_ROLE,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=27,
  serialized_end=245,
)


_AGENTCONTAINER = _descriptor.Descriptor(
  name='AgentContainer',
  full_name='gaiachain.AgentContainer',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='entries', full_name='gaiachain.AgentContainer.entries', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=247,
  serialized_end=298,
)

_AGENT.fields_by_name['role'].enum_type = _AGENT_ROLE
_AGENT_ROLE.containing_type = _AGENT
_AGENTCONTAINER.fields_by_name['entries'].message_type = _AGENT
DESCRIPTOR.message_types_by_name['Agent'] = _AGENT
DESCRIPTOR.message_types_by_name['AgentContainer'] = _AGENTCONTAINER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Agent = _reflection.GeneratedProtocolMessageType('Agent', (_message.Message,), {
  'DESCRIPTOR' : _AGENT,
  '__module__' : 'agent_pb2'
  # @@protoc_insertion_point(class_scope:gaiachain.Agent)
  })
_sym_db.RegisterMessage(Agent)

AgentContainer = _reflection.GeneratedProtocolMessageType('AgentContainer', (_message.Message,), {
  'DESCRIPTOR' : _AGENTCONTAINER,
  '__module__' : 'agent_pb2'
  # @@protoc_insertion_point(class_scope:gaiachain.AgentContainer)
  })
_sym_db.RegisterMessage(AgentContainer)


# @@protoc_insertion_point(module_scope)
