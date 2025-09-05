## 0.65.13 (2025-09-04)

### Fix

- **ModelGenerator**: Add `pass` keyword when there are no fields (#891)

## 0.65.12 (2025-07-18)

### Fix

- add some missing types (#877)

## 0.65.11 (2025-06-26)

### Fix

- **ModelGenerator**: Rename fields named after Python keywords (#870)

## 0.65.10 (2025-03-10)

### Fix

- **AvroRecord**: deserialize properly union when they are encoded using avro-bynary. Related to #849 (#853)

## 0.65.9 (2025-02-28)

### Fix

- **ModelGenerator**: render description when doc is present in schema and the model is pydantic related. Related to #837 (#843)

## 0.65.8 (2025-02-04)

### Fix

- **ModelGenerator**: generate proper default value for a first time defined record when it has one. Closes #829 (#835)

## 0.65.7 (2024-12-12)

### Fix

- support Python 3.13 in is_annotated (#817)

## 0.65.6 (2024-12-06)

### Fix

- make sure that metadata is not deleted when schemas are calculated more than once. Closes #799 (#815)

## 0.65.5 (2024-12-02)

### Fix

- serialization whit schema inheritance. Closes #800 (#810)

## 0.65.4 (2024-11-28)

### Fix

- Model and Parser protocols added (#801)

## 0.65.3 (2024-11-18)

### Fix

- **TimedeltaField**: fix timedelta fastavro serialization so it doesn't break in union types (#797)

## 0.65.2 (2024-11-13)

### Fix

- generate proper default values when reusing Enums types (#796)

## 0.65.1 (2024-11-13)

### Fix

- model generatation fixed when field name and field type hint clashes on arrays and maps (#795)

## 0.65.0 (2024-11-06)

### Feat

- support timedelta serialization to `double` seconds (#793)

## 0.64.2 (2024-10-24)

### Fix

- **ModelGenerator**: ModelRepresentation and EnumRepresentation added to make model generation simpler. More name clashing cases fixed (#783)

## 0.64.1 (2024-10-23)

### Fix

- dc-avro dependency (#782)

## 0.64.0 (2024-10-23)

### Fix

- generate date defaults consistently in python model generation (#780)

## 0.63.10 (2024-10-22)

### Fix

- python38 support dropped (#781)

## 0.63.9 (2024-10-21)

### Fix

- generate proper Model when there is name clashe between field name and type hints. Closes #769 (#778)

## 0.63.8 (2024-10-21)

### Fix

- dc-avro dependency updated (#779)

## 0.63.7 (2024-10-17)

### Fix

- AttributeError exception raised when trying to generate schema from AvroModel itself and not a subclass of it. Closes #739 (#777)

## 0.63.6 (2024-10-16)

### Fix

- model generation simplified. Closes #746 (#776)

## 0.63.5 (2024-10-11)

### Fix

- make context optional during dezerialization. Serialization utils included in docs. SerializationType included (#774)

## 0.63.4 (2024-10-10)

### Refactor

- Module schema_generator renamed to main. Some type hints improvements (#773)

## 0.63.3 (2024-10-09)

### Fix

- serialization improvements for nested unions. Related to #763 (#770)

## 0.63.2 (2024-09-27)

### Fix

- serialiaze properly unions when types are similar. Closes #749 (#751)

## 0.63.1 (2024-09-24)

### Fix

- Explicit __all__ to make mypy happy (#757)

## 0.63.0 (2024-09-13)

### Feat

- add serialization support for AvroRecord (faust.Record). Closes #743 (#744)

## 0.62.11 (2024-08-26)

### Fix

- Implemented nested logicalType check (#734)

## 0.62.10 (2024-08-23)

### Fix

- scaped apostrophe when original_schema is render in model. Closes #725 (#728)

## 0.62.9 (2024-08-22)

### Fix

- fallback to native types if custom logicalTypes are defined when rendering Model. Closes #707 and closes #209 (#724)

## 0.62.8 (2024-08-21)

### Fix

- case schemas with unions. Closes #700 (#723)

## 0.62.7 (2024-08-15)

### Fix

- python-dateutil dependency updated in pyproject (#720)

## 0.62.6 (2024-08-14)

### Fix

- inflector dependency replaced by inflection. First steps to publish library to Conda. Related to #706 (#719)

## 0.62.5 (2024-08-13)

### Fix

- extra option with cli added in pyproject. Requirements fixed. Closes #711 (#718)

## 0.62.4 (2024-08-09)

### Fix

- Always reuse the rendered type when type is same (#710). Closes #709

## 0.62.3 (2024-08-08)

### Fix

- incorrect casing when rendering fields and enums  (#694). Closes #693 and #692

## 0.62.2 (2024-07-24)

### Fix

- render avro enums in isolation. Closes #664 (#690)

## 0.62.1 (2024-07-22)

### Fix

- serdes speed-ups (#677)

## 0.62.0 (2024-07-19)

### Feat

- enum type level default intruduced. Closes #665 (#682)

## 0.61.0 (2024-07-10)

### Feat

- render enum as (str, enum.Enum) (#637) (#652)

## 0.60.2 (2024-06-07)

### Fix

- add aliases to field when field name is not a valid identifier. Related to #628 (#654)

## 0.60.1 (2024-05-30)

### Fix

- missing dependency python-dateutil added. Closes #644 (#645)

## 0.60.0 (2024-05-29)

### Feat

- missing dacite hooks added in order to parse_obj in a proper way. Related to #638 (#643)

## 0.59.1 (2024-05-24)

### Fix

- generate proper python identifiers when generating model from schemas. Related to #628 (#639)

## 0.59.0 (2024-04-19)

### Feat

- convert_literal_to_enum option added. Closes #596 (#608)

## 0.58.2 (2024-04-12)

### Fix

- custom types with extra annotation. Closes #598 (#601)

## 0.58.1 (2024-04-11)

### Fix

- add Enum symbol validation (#599)

## 0.58.0 (2024-03-28)

### Feat

- Support for Pydantic field alias and serialization_alias (#583). Closes #293

## 0.57.5 (2024-03-26)

### Fix

- improve pydantic model translation (#582)

## 0.57.4 (2024-03-15)

### Fix

- do not force pascalcase for enum names. Closes #544 (#571)

## 0.57.3 (2024-03-14)

### Fix

- add inner names suppor for complex types. Closes #534 and related to #544 (#570)

## 0.57.2 (2024-03-11)

### Fix

- model generator refactored (#569)

## 0.57.1 (2024-02-22)

### Fix

- pass to fastavro all schemas in a single call (#553)

## 0.57.0 (2024-02-16)

### Feat

- Possibility for original schema string in objects Meta class. (#545)

## 0.56.2 (2024-02-12)

### Fix

- Install typing-extensions when using Python > 3.8 (#541)

## 0.56.1 (2024-01-30)

### Fix

- Optional[Literal] type fixed. Closes #518 (#528)

## 0.56.0 (2024-01-19)

### Feat

- support for pydantic date and datetime added (#517)

## 0.55.1 (2024-01-16)

### Fix

- bump inflector version for python3.12 support (#519)

## 0.55.0 (2024-01-16)

### Feat

- exclude_default option added in metadata. Closes #400 (#513)

## 0.54.2 (2023-12-12)

### Fix

- kwarg typing in AvroModel (#488)

## 0.54.1 (2023-12-07)

### Fix

- syntax warning in FakeStub docstring (#486)

## 0.54.0 (2023-12-01)

### Feat

- property extra_allowed_default_types added to Field. Closes #457 (#481)

## 0.53.1 (2023-11-15)

### Fix

- simplify faker stub code (#471)

## 0.53.0 (2023-11-03)

### Feat

- add pydantic v2 support. Closes #415 (#455)

## 0.52.1 (2023-10-09)

### Fix

- add fake() support to Literal field type (#451)

## 0.52.0 (2023-09-28)

### Feat

- add support for typing.Literal (#435).

## 0.51.0 (2023-09-20)

### Feat

- **pydantic-v2**: First steps to support pydantic v2. Namespace dataclasses_avroschame.pydantic added. All AvroModel fields now are private (#427)

## 0.50.2 (2023-09-19)

### Fix

- Add typing-extensions to python 3.8 (#432)

## 0.50.1 (2023-09-19)

### Fix

- Resolve issues with raw `None` annotation (#433). Closes #424

## 0.50.0 (2023-09-13)

### Feat

- add support for pydantic custom classes as fields (#420)

## 0.49.0 (2023-09-12)

### Feat

- option to exclude fields on the output schema added. (#423)

## 0.48.1 (2023-09-12)

### Fix

- respect enum symbols order when generating models from schemas. Related to #413 (#422)

## 0.48.0 (2023-09-11)

### BREAKING CHANGE

- drop python 3.7 support (#414)

## 0.47.3 (2023-09-06)

### Fix

- Model/code generator when enum has namespaces. Closes #406 (#410)

## 0.47.2 (2023-08-30)

### Fix

- field ordering when field has metadata but not a default value. Closes #401 (#403)

## 0.47.1 (2023-08-30)

### Fix

- do not uppercase enums keys when the key already exist. Closes #399 (#402)

## 0.47.0 (2023-08-28)

### Feat

- Make Faker an optional dependency. (#391)

## 0.46.3 (2023-08-25)

### Fix

- dependencies updated (#393)

## 0.46.2 (2023-08-15)

### Fix

- record fields avro schema creation (#382) (#383)

## 0.46.1 (2023-08-14)

### Fix

- schema generation with optional Enum fields (#386)

## 0.46.0 (2023-08-14)

### Feat

- support pydantic constrained int fields (#379)

## 0.45.1 (2023-07-27)

### Fix

- default factory in order to get proper default values. Closes #365

## 0.45.0 (2023-07-18)

### Feat

- field_order property added to class Meta. Closes #345 (#369)

## 0.44.0 (2023-07-06)

### Feat

- pydantic fields added. Closes #328

## 0.43.10 (2023-06-29)

### Fix

- model generator when fields have metadata. Closes #348 (#355)

## 0.43.9 (2023-06-19)

### Fix

- pydantic nested schema serialization (#346)

## 0.43.8 (2023-06-15)

### Fix

- stringcase replaced by casefy. Closes #341 (#347)

## 0.43.7 (2023-06-13)

### Fix

- Fix typo in kwargs typehint for AvroBaseModel.fake (#340)

## 0.43.6 (2023-05-30)

### Fix

- ci process (#336)

## 0.43.5 (2023-05-30)

### Fix

- update dependencies and bump version (#334)

## 0.43.4 (2023-05-26)

### Fix

- proper schema generation when primitive types are defined types. Closes #330 (#332)

## 0.43.3 (2023-05-25)

### Fix

- dict conversion of AvroBaseModel. Closes #324 (#331)

## 0.43.2 (2023-05-25)

### Fix

- deserialization with more than tow layers. Closes #326 (#329)

## 0.43.1 (2023-05-19)

### Fix

- excluded pydantic.Fields should be used on avro serialization. Closes #314 (#322)

## 0.43.0 (2023-04-26)

### Feat

- AvroRecord added in order to make simpler faust usage. Closes #281 (#303)

## 0.42.2 (2023-04-24)

### Fix

- pydantic and faust-streaming optional dependencies. Remove pytz as dependency. Closes #292 (#297)

## 0.42.1 (2023-04-24)

### Fix

- **typing**: incorrect type annotations in avrodantic.py (#302)

## 0.42.0 (2023-04-21)

### Feat

- TupleField added in order to deserialize typing.Tuple as tuples rather than list. Closes #291 (#296)

## 0.41.2 (2023-04-20)

### Fix

- dev dependencies updated (#294)

## 0.41.1 (2023-04-06)

### Fix

- dependencies updated. Model generator documentation updated (#285)

## 0.41.0 (2023-04-06)

### BREAKING CHANGE

- types.Decimal has been replaced by condecimal (Annotated[decimal.Decimal]). Closes #260 (#282)

## 0.40.0 (2023-03-29)

### Fix

- correctly generate enum default values (#275)
- correctly generate type annotations

fix: do not generate default dataclass docstrings

fix: datetime model generation

the previous implementation did not roundtrip

feat: render docstrings in generated classes

fix: correct union and optional conversion

test: add avsc -> python -> avsc roundtrip test

fix: properly handle aliases in the model generator

tests: add coverage for single-type unions model generation

Co-authored-by: Maximilian Hils <git@maximilianhils.com>

## 0.39.3 (2023-03-29)

### Fix

- include matadata when using pydantic.Field with AvroBaseMode. Closes #263 (#274)

## 0.39.2 (2023-03-28)

### Fix

- use `extras` in a correct way. Closes #272 (#273)

## 0.39.1 (2023-03-27)

### Fix

- dependencies updated. Closes #270 (#271)

## 0.39.0 (2023-03-24)

### Feat

- support for typing.Annotated added (#264)

## 0.38.1 (2023-03-22)

### Fix

- dc-avro dependency (#262)

## 0.38.0 (2023-03-22)

## v0.37.5 (2023-03-17)

### Fix

- avro schema generation should always return the same result. Close #254 (#255)

## v0.37.4 (2023-03-06)

### Fix

- release v0.37.3 -> v0.37.4
- exception NameSpaceRequiredException removed. Close #246 (#253)

## v0.37.3 (2023-03-06)

### Fix

- dependencies and documentation (#252)

## v0.37.2 (2023-03-02)

### Fix

- use UUID type instead of function uuid4 (#251)

## v0.37.1 (2023-02-24)

### Fix

- use pydantic UUID4 when generating pydantic models. (#247)

## v0.37.0 (2023-02-22)

### Feat

- dacite custom config added to class Meta. Closes #242 (#245)

## v0.36.3 (2023-02-16)

### Fix

- ListField fake generation when it contains Optional. Closes #232 (#244)

## v0.36.2 (2023-02-14)

### Fix

- do not persist the schema when the parent class is not an AvroModel. Closes #241 (#243)

### Perf

- ruff added in order to replace isort and flake8 (#238)

## v0.36.1 (2023-01-19)

### Fix

- use pydantic condecimal when generating pydantic models. Closes #234 (#237)
- model generator with only decimal fields. Closes #233 (#236)

## v0.36.0 (2023-01-18)

### Feat

- Generate a Python module from multiple schemas (#235)

## v0.35.0 (2023-01-10)

### Feat

- model generator added (#227)
- self relationship schema generation

feat: logicalTypes model generation

feat: logical types model generator

fix: field order, pascal case for class names

fix: add class Meta support

Co-authored-by: Marcos Schroh <marcos.schroh@kpn.com>

## v0.34.6 (2023-01-06)

### Fix

- use namespaces when an enum is used multiple times in a class. Cases should not apply to enum names. Closes #221 (#231)

## v0.34.5 (2023-01-06)

### Fix

- schema generation with optional enum when using pydantic. Closes #229 (#230)

## v0.34.4 (2023-01-04)

### Fix

- fake generation with optional user defined types (#228)

## v0.34.3 (2022-12-15)

### Fix

- serialize decimal fields. Closes #222 (#224)

## v0.34.2 (2022-11-18)

### Fix

- pydantic fake and nested json serialization (#219)

## v0.34.1 (2022-11-11)

### Fix

- include field metadata when using faust records. Closes #217 (#218)

## v0.34.0 (2022-11-01)

### Feat

- types.UnionType support added (#213)

## v0.33.0 (2022-11-01)

## v0.32.3 (2022-10-31)

### Fix

- update to latest fastavro. logical types fixed (#214)

## v0.32.2 (2022-10-25)

### Fix

- nested enums serialization. Closes #208 (#211)

## v0.32.1 (2022-10-13)

### Perf

- use python __slots__ (#206)

## v0.32.0 (2022-10-13)

### Feat

- provide data to the fake functionality (#205)

## v0.31.3 (2022-10-07)

### Fix

- utils refactor. @dataclass decorator included in all code examples. Inheritance example added. Closes #202 (#204)

## v0.31.2 (2022-10-03)

### Fix

- UnknownType on serialization with intermediates schemas. Closes #199 (#201)

## v0.31.1 (2022-09-30)

### Fix

- name collision on splittes schema usage. Close #196 (#198)

## v0.31.0 (2022-09-23)

### Feat

- micro precision added to time and datetime types (#197)

## v0.30.3 (2022-08-05)

### Fix

- mypy issues (#186)

## v0.30.2 (2022-08-04)

### Fix

- Do not use name and type from metadata in avro schema (#188) (#189)

## v0.30.1 (2022-08-02)

### Fix

- fastavro dependency updated. Close #184 (#187)

## v0.30.0 (2022-05-18)

## v0.29.2 (2022-05-06)

## v0.29.1 (2022-04-15)

### Fix

- nested metadata not respected. closes #171 (#172)

## v0.29.0 (2022-04-08)

### Fix

- create nested schema resolution directly from dictionaries (#170)

## v0.28.1 (2022-04-05)

### Fix

- alias for nested items (#169)

## v0.28.0 (2022-03-23)

### Feat

- pydantic support added (#163)

## v0.27.2 (2022-03-23)

### Fix

- rebuild cache (#164)

## v0.27.1 (2022-03-22)

## v0.27.0 (2022-02-18)

### Feat

- add enum support (#153)

## v0.26.1 (2021-12-07)

### Feat

- manual job trigger (#146)

### Fix

- use root reference to generate valid schemas in multiple inheritance levels (#148)
- cache and release expresion (#147)

## v0.26.0 (2021-12-06)

### Feat

- validate method added (#144)

### Fix

- some type checks (#143)
- mkdocs styles (#141)

## v0.25.3 (2021-11-26)

### Fix

- generate valid avro schemas when inheritance has multiple levels (#140)
- api get_fields now returns all rendered fields (#134)

## v0.25.1 (2021-10-06)

## v0.25.0 (2021-09-27)

### Feat

- case schemas. Closes #79 (#95)

### Fix

- new style type annotations don't work for containers and maps (#122)
- possible crash if no docs (#123)

## v0.24.0 (2021-09-24)

### Feat

- add `int` and `float` Avro type support (#119)

## v0.23.2 (2021-09-04)

### Fix

- use namespaces on repeated user types with complex types (#117)

## v0.23.1 (2021-09-03)

### Fix

- using namespaces for repeated nested types in arrays and maps (#116)

## v0.23.0 (2021-08-26)

### Feat

- use namespaces for repeated types (#115)

## v0.22.1 (2021-07-05)

## v0.22.0 (2021-06-30)

### Feat

- alias nested schemas added (#110)

## v0.21.0 (2021-06-17)

### Fix

- github CI added (#106)

## v0.20.4 (2021-05-05)

## v0.20.3 (2021-04-29)

### Fix

- dependencies updated (#97)
- Improve error message in unknown type (#94)
- generators fixtures replaced with container. Close #70 (#91)

## v0.20.2 (2021-01-27)

### Fix

- avro-json serialization with defaults (#89)

## v0.20.1 (2020-12-04)

## v0.20.0 (2020-11-24)

## v0.19.0 (2020-11-12)

### Fix

- doc updated

## v0.18.0 (2020-10-10)

### Fix

- correct name generation for nested records (#81)

## v0.17.0 (2020-09-04)

### Feat

- fake class instances generation added (#77)

## v0.16.0 (2020-08-27)

### Fix

- isort (#71)

## v0.15.2 (2020-08-25)

### Fix

- pytz added as requirement (#69)

## v0.15.1 (2020-08-22)

### Fix

- include UUID as field type (#68)

## v0.15.0 (2020-08-16)

### Fix

- use generic to_avro method for logical types (#66)
- replace 'null' str with avro null (json) (#65)

### Perf

- check for dataclass.MISSING removed. coverage increased up to 99% (#61)

## v0.14.6 (2020-07-11)

### Fix

- field SelfReference fixed (#59)

## v0.14.5 (2020-07-09)

### Fix

- null should not be included when a default value is defined (#58)

## v0.14.4 (2020-07-03)

### Fix

- union with complex type fixed. union with optional types fixed. close #51. (#56)

## v0.14.3 (2020-06-29)

### Fix

- refactor logical types (#54)
- support for aware datetime added (#53)
- serialization for complex types (#49)

## v0.14.2 (2020-06-16)

### Fix

- pytest dependency updated (#46)

## v0.14.1 (2020-06-09)

### Fix

- bytes type fixed (#42)

## v0.14.0 (2020-06-01)

## v0.13.1 (2020-05-28)

### Fix

- enum field refactored in order to include other enum attributes (#37)

## v0.13.0 (2020-05-25)

### Feat

- generate json payload from class instance accroding to the avro schema generated (#36)

## v0.12.0 (2020-05-25)

### Fix

- schema-generator import improved (#35)

## v0.11.1 (2020-05-20)

### Feat

- serialization added (#34)

### Fix

- fastavro included as dependencie
- development scripts updated. (#33)

## v0.10.0 (2020-02-16)

### Feat

- fixed type support added (#32)

## v0.9.0 (2020-01-24)

### Fix

- isort added. more mypy types added. WIP mypy checks (#30)
- Correct license to MIT in setup.py (#29)

## v0.8.0 (2020-01-06)

## v0.7.4 (2019-11-21)

### Fix

- **Avro-Array**: Handle union inside array field. Closes #21

## v0.7.3 (2019-11-16)

### Fix

- **typing.Dict**: Include LogicalTypes as values
- **typing.List**: Include LogicalTypes as items
- Code refactor and first steps to support logicaltypes in sequences and maps

## v0.7.2 (2019-11-07)

### Fix

- Union type allow logical and primitive types

## v0.7.1 (2019-10-25)

### Fix

- Support for Sequences and Mapping added

## v0.7.0 (2019-10-23)

### Feat

- Generate Avro Schemas from Faust Records

## v0.6.1 (2019-10-21)

### Fix

- Validate default values when the avro schema is generated

## v0.6.0 (2019-10-17)

### Feat

- Union support added

### Fix

- mkdocs fixed

## v0.5.0 (2019-10-13)

### Feat

- **LogicalTypes**: Support for Date, Time, Datetime and UUID added

## v0.4.1 (2019-10-11)

### Fix

- Fields refactor

## v0.4.0 (2019-10-05)

### Feat

- Self relationship OneToOne added
- Self relationship OneToMany added
- Self relationship OneToMany finished. Factory Pattern used in SchemaGenarator and AvroSchemaDefinition

## v0.3.1 (2019-09-05)

## v0.3.0 (2019-09-03)

### Feat

- Singular names are generated for array, map chilndren's namea nd enum

## v0.2.0 (2019-09-02)

### Feat

- OneToMany schema relationship added.

## v0.1.1 (2019-09-02)

### Feat

- One To Many relationship added
- One to One schema relationship added
- Travis added

### Fix

- Default values for Map and Array
- Map, Array and Enum types fixed. Schema Parse tests added with fastavro
- License added
- mkdocs links updated

## v0.1.0 (2019-08-29)

### Feat

- clean & publish scrips added. Docs added
- avro_schema method added to SchemaGenerator class. Doc added.
- Aliases and Namespaces avro check added

### Fix

- clean & publish scripts should be executables
- Exclude default type only when is a tuple
- The avro schema returned should be string, not a python dict.
- Package renamed to dataclasses_avroschema
