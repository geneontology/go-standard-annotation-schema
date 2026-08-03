from __future__ import annotations

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer
)


metamodel_version = "1.11.0"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias = True,
        validate_by_name = True,
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )





class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'go_standard_annotation_schema',
     'default_range': 'string',
     'description': 'LinkML schema for GO Standard Annotations',
     'id': 'https://w3id.org/geneontology/go-standard-annotation-schema',
     'license': 'BSD-3-Clause',
     'name': 'go-standard-annotation-schema',
     'prefixes': {'go_standard_annotation_schema': {'prefix_prefix': 'go_standard_annotation_schema',
                                                    'prefix_reference': 'https://w3id.org/geneontology/go-standard-annotation-schema/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'schema': {'prefix_prefix': 'schema',
                             'prefix_reference': 'http://schema.org/'},
                  'shex': {'prefix_prefix': 'shex',
                           'prefix_reference': 'http://www.w3.org/ns/shex#'},
                  'xsd': {'prefix_prefix': 'xsd',
                          'prefix_reference': 'http://www.w3.org/2001/XMLSchema#'}},
     'see_also': ['https://geneontology.github.io/go-standard-annotation-schema'],
     'settings': {'local_id': {'setting_key': 'local_id',
                               'setting_value': '[A-Za-z0-9_\\-.:/]+'},
                  'prefix': {'setting_key': 'prefix',
                             'setting_value': '[A-Za-z][A-Za-z0-9_\\-.]*'}},
     'source_file': 'tmp/go_standard_annotation_schema_materialized.yaml',
     'title': 'GO Standard Annotation Schema',
     'types': {'boolean': {'base': 'Bool',
                           'description': 'A binary (true or false) value',
                           'exact_mappings': ['schema:Boolean'],
                           'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                           'name': 'boolean',
                           'notes': ['If you are authoring schemas in LinkML YAML, '
                                     'the type is referenced with the lower case '
                                     '"boolean".'],
                           'repr': 'bool',
                           'uri': 'xsd:boolean'},
               'curie': {'base': 'Curie',
                         'comments': ['in RDF serializations this MUST be expanded '
                                      'to a URI',
                                      'in non-RDF serializations MAY be serialized '
                                      'as the compact representation'],
                         'conforms_to': 'https://www.w3.org/TR/curie/',
                         'description': 'a compact URI',
                         'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                         'name': 'curie',
                         'notes': ['If you are authoring schemas in LinkML YAML, '
                                   'the type is referenced with the lower case '
                                   '"curie".'],
                         'repr': 'str',
                         'uri': 'xsd:string'},
               'date': {'base': 'XSDDate',
                        'description': 'a date (year, month and day) in an '
                                       'idealized calendar',
                        'exact_mappings': ['schema:Date'],
                        'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                        'name': 'date',
                        'notes': ["URI is dateTime because OWL reasoners don't "
                                  'work with straight date or time',
                                  'If you are authoring schemas in LinkML YAML, '
                                  'the type is referenced with the lower case '
                                  '"date".'],
                        'repr': 'str',
                        'uri': 'xsd:date'},
               'date_or_datetime': {'base': 'str',
                                    'description': 'Either a date or a datetime',
                                    'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                                    'name': 'date_or_datetime',
                                    'notes': ['If you are authoring schemas in '
                                              'LinkML YAML, the type is referenced '
                                              'with the lower case '
                                              '"date_or_datetime".'],
                                    'repr': 'str',
                                    'uri': 'linkml:DateOrDatetime'},
               'datetime': {'base': 'XSDDateTime',
                            'description': 'The combination of a date and time',
                            'exact_mappings': ['schema:DateTime'],
                            'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                            'name': 'datetime',
                            'notes': ['If you are authoring schemas in LinkML '
                                      'YAML, the type is referenced with the lower '
                                      'case "datetime".'],
                            'repr': 'str',
                            'uri': 'xsd:dateTime'},
               'decimal': {'base': 'Decimal',
                           'broad_mappings': ['schema:Number'],
                           'description': 'A real number with arbitrary precision '
                                          'that conforms to the xsd:decimal '
                                          'specification',
                           'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                           'name': 'decimal',
                           'notes': ['If you are authoring schemas in LinkML YAML, '
                                     'the type is referenced with the lower case '
                                     '"decimal".'],
                           'uri': 'xsd:decimal'},
               'double': {'base': 'float',
                          'close_mappings': ['schema:Float'],
                          'description': 'A real number that conforms to the '
                                         'xsd:double specification',
                          'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                          'name': 'double',
                          'notes': ['If you are authoring schemas in LinkML YAML, '
                                    'the type is referenced with the lower case '
                                    '"double".'],
                          'uri': 'xsd:double'},
               'eco_identifier': {'description': 'An identifier of an ECO term.',
                                  'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                                  'name': 'eco_identifier',
                                  'structured_pattern': {'interpolated': True,
                                                         'partial_match': False,
                                                         'syntax': 'ECO:{local_id}'},
                                  'typeof': 'external_identifier'},
               'external_identifier': {'description': 'An identifier of an object '
                                                      'from an external source, '
                                                      'such as a gene product, an\n'
                                                      'ontology term, or a '
                                                      'publication.',
                                       'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                                       'name': 'external_identifier',
                                       'structured_pattern': {'interpolated': True,
                                                              'partial_match': False,
                                                              'syntax': '{prefix}:{local_id}'},
                                       'typeof': 'string'},
               'float': {'base': 'float',
                         'description': 'A real number that conforms to the '
                                        'xsd:float specification',
                         'exact_mappings': ['schema:Float'],
                         'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                         'name': 'float',
                         'notes': ['If you are authoring schemas in LinkML YAML, '
                                   'the type is referenced with the lower case '
                                   '"float".'],
                         'uri': 'xsd:float'},
               'go_identifier': {'description': 'An identifier of a GO term.',
                                 'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                                 'name': 'go_identifier',
                                 'structured_pattern': {'interpolated': True,
                                                        'partial_match': False,
                                                        'syntax': 'GO:{local_id}'},
                                 'typeof': 'external_identifier'},
               'integer': {'base': 'int',
                           'description': 'An integer',
                           'exact_mappings': ['schema:Integer'],
                           'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                           'name': 'integer',
                           'notes': ['If you are authoring schemas in LinkML YAML, '
                                     'the type is referenced with the lower case '
                                     '"integer".'],
                           'uri': 'xsd:integer'},
               'jsonpath': {'base': 'str',
                            'conforms_to': 'https://www.ietf.org/archive/id/draft-goessner-dispatch-jsonpath-00.html',
                            'description': 'A string encoding a JSON Path. The '
                                           'value of the string MUST conform to '
                                           'JSON Point syntax and SHOULD '
                                           'dereference to zero or more valid '
                                           'objects within the current instance '
                                           'document when encoded in tree form.',
                            'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                            'name': 'jsonpath',
                            'notes': ['If you are authoring schemas in LinkML '
                                      'YAML, the type is referenced with the lower '
                                      'case "jsonpath".'],
                            'repr': 'str',
                            'uri': 'xsd:string'},
               'jsonpointer': {'base': 'str',
                               'conforms_to': 'https://datatracker.ietf.org/doc/html/rfc6901',
                               'description': 'A string encoding a JSON Pointer. '
                                              'The value of the string MUST '
                                              'conform to JSON Point syntax and '
                                              'SHOULD dereference to a valid '
                                              'object within the current instance '
                                              'document when encoded in tree form.',
                               'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                               'name': 'jsonpointer',
                               'notes': ['If you are authoring schemas in LinkML '
                                         'YAML, the type is referenced with the '
                                         'lower case "jsonpointer".'],
                               'repr': 'str',
                               'uri': 'xsd:string'},
               'ncbi_taxon_identifier': {'description': 'An identifier of a taxon '
                                                        'from the NCBI Taxonomy '
                                                        'database.',
                                         'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                                         'name': 'ncbi_taxon_identifier',
                                         'structured_pattern': {'interpolated': True,
                                                                'partial_match': False,
                                                                'syntax': 'NCBITaxon:{local_id}'},
                                         'typeof': 'external_identifier'},
               'ncname': {'base': 'NCName',
                          'description': 'Prefix part of CURIE',
                          'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                          'name': 'ncname',
                          'notes': ['If you are authoring schemas in LinkML YAML, '
                                    'the type is referenced with the lower case '
                                    '"ncname".'],
                          'repr': 'str',
                          'uri': 'xsd:string'},
               'nodeidentifier': {'base': 'NodeIdentifier',
                                  'description': 'A URI, CURIE or BNODE that '
                                                 'represents a node in a model.',
                                  'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                                  'name': 'nodeidentifier',
                                  'notes': ['If you are authoring schemas in '
                                            'LinkML YAML, the type is referenced '
                                            'with the lower case '
                                            '"nodeidentifier".'],
                                  'repr': 'str',
                                  'uri': 'shex:nonLiteral'},
               'objectidentifier': {'base': 'ElementIdentifier',
                                    'comments': ['Used for inheritance and type '
                                                 'checking'],
                                    'description': 'A URI or CURIE that represents '
                                                   'an object in the model.',
                                    'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                                    'name': 'objectidentifier',
                                    'notes': ['If you are authoring schemas in '
                                              'LinkML YAML, the type is referenced '
                                              'with the lower case '
                                              '"objectidentifier".'],
                                    'repr': 'str',
                                    'uri': 'shex:iri'},
               'sparqlpath': {'base': 'str',
                              'conforms_to': 'https://www.w3.org/TR/sparql11-query/#propertypaths',
                              'description': 'A string encoding a SPARQL Property '
                                             'Path. The value of the string MUST '
                                             'conform to SPARQL syntax and SHOULD '
                                             'dereference to zero or more valid '
                                             'objects within the current instance '
                                             'document when encoded as RDF.',
                              'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                              'name': 'sparqlpath',
                              'notes': ['If you are authoring schemas in LinkML '
                                        'YAML, the type is referenced with the '
                                        'lower case "sparqlpath".'],
                              'repr': 'str',
                              'uri': 'xsd:string'},
               'string': {'base': 'str',
                          'description': 'A character string',
                          'exact_mappings': ['schema:Text'],
                          'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                          'name': 'string',
                          'notes': ['In RDF serializations, a slot with range of '
                                    'string is treated as a literal or type '
                                    'xsd:string. If you are authoring schemas in '
                                    'LinkML YAML, the type is referenced with the '
                                    'lower case "string".'],
                          'uri': 'xsd:string'},
               'time': {'base': 'XSDTime',
                        'description': 'A time object represents a (local) time of '
                                       'day, independent of any particular day',
                        'exact_mappings': ['schema:Time'],
                        'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                        'name': 'time',
                        'notes': ['URI is dateTime because OWL reasoners do not '
                                  'work with straight date or time',
                                  'If you are authoring schemas in LinkML YAML, '
                                  'the type is referenced with the lower case '
                                  '"time".'],
                        'repr': 'str',
                        'uri': 'xsd:time'},
               'uri': {'base': 'URI',
                       'close_mappings': ['schema:URL'],
                       'comments': ['in RDF serializations a slot with range of '
                                    'uri is treated as a literal or type '
                                    'xsd:anyURI unless it is an identifier or a '
                                    'reference to an identifier, in which case it '
                                    'is translated directly to a node'],
                       'conforms_to': 'https://www.ietf.org/rfc/rfc3987.txt',
                       'description': 'a complete URI',
                       'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                       'name': 'uri',
                       'notes': ['If you are authoring schemas in LinkML YAML, the '
                                 'type is referenced with the lower case "uri".'],
                       'repr': 'str',
                       'uri': 'xsd:anyURI'},
               'uriorcurie': {'base': 'URIorCURIE',
                              'description': 'a URI or a CURIE',
                              'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                              'name': 'uriorcurie',
                              'notes': ['If you are authoring schemas in LinkML '
                                        'YAML, the type is referenced with the '
                                        'lower case "uriorcurie".'],
                              'repr': 'str',
                              'uri': 'xsd:anyURI'}}} )


class StandardAnnotation(ConfiguredBaseModel):
    """
    An association between a gene product and a GO term, with an evidence code, a
    reference to support the association, and other data associated with the gene
    product or the annotation.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema'})

    db_object_id: str = Field(default=..., description="""A unique identifier for the item being annotated.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardAnnotation']} })
    negation: Optional[bool] = Field(default=None, description="""A boolean indicating whether the annotation is negated.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardAnnotation']} })
    relation: str = Field(default=..., description="""Relation from the Relation Ontology that describe how the annotated biological
entity relates to the GO term with which it is associated.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardAnnotation'],
         'todos': ['The GPAD spec says that the "relation used SHOULD come from the '
                   'allowed gene-product-to-term relations". Decide whether to enforce '
                   'this in the schema via an enum.']} })
    ontology_class_id: str = Field(default=..., description="""The GO identifier for the term attributed to the DB object ID.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardAnnotation']} })
    references: list[str] = Field(default=..., description="""One or more unique identifiers for a single source cited as an authority for the
attribution of the GO ID to the DB object ID. This may be a literature reference
or a database record. Valid references are one of: PubMed, DOI, GO_REF, MOD
reference.""", min_length=1, json_schema_extra = { "linkml_meta": {'domain_of': ['StandardAnnotation']} })
    evidence_type: str = Field(default=..., description="""The Evidence & Conclusion Ontology (ECO) identifier for the evidence code that
supports the association between the DB object ID and the GO term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardAnnotation']} })
    with_or_from: Optional[list[str]] = Field(default=None, description="""Used with specific ECO codes to capture an additional identifier supporting the
evidence for the annotation. For example, it can identify another gene product to
which the annotated gene product is similar (ISS) or interacts with (IPI).
Population of the With/From is mandatory for certain evidence codes.""", json_schema_extra = { "linkml_meta": {'comments': ['Cardinality must be 0 for evidence codes IDA, TAS, NAS, or ND',
                      'Cardinality must be 1, >1 for IEA, IC, IGI, IPI, ISS & child '
                      'terms of ISS'],
         'domain_of': ['StandardAnnotation'],
         'todos': ['The GPAD spec makes a distinction between pipe- and '
                   'comma-separated lists of With/From values. Decide if and how this '
                   'should be represented in the schema.']} })
    interacting_taxon: Optional[list[str]] = Field(default=None, description="""Taxonomic identifier for interacting organism to be used only in conjunction with
terms that have the biological process term 'GO:0044419 biological process
involved in interspecies interaction between organisms' or the cellular component
term 'GO:0018995 host cellular component' as an ancestor. Identifiers must come
from NCBI Taxonomy database.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardAnnotation']} })
    annotation_date: date = Field(default=..., description="""Date on which the annotation was made""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardAnnotation'],
         'todos': ['The GPAD file description says that this is a date in the format '
                   '`YYYY-MM-DD`. The spec says that it is a date or datetime. Decide '
                   'whether to permit date, datetime, or both.']} })
    assigned_by: str = Field(default=..., description="""The database which made the annotation one of the values from the set of GOC
groups; used for tracking the source of an individual annotation.""", json_schema_extra = { "linkml_meta": {'comments': ['Value may differ from the DB:DB Object ID column. Any '
                      'annotation that is made by one database and incorporated into '
                      'another retains the original value.'],
         'domain_of': ['StandardAnnotation']} })
    annotation_extensions: Optional[list[AnnotationExtension]] = Field(default=None, description="""Annotation extensions allow GO terms in standard annotations to be further
specified, using gene products, chemicals, cell types, anatomical structures, to
provide additional biological context. The cross-reference is prefaced by an
appropriate relationship from the Relation Ontology.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardAnnotation'],
         'todos': ['The GPAD spec makes a distinction between pipe- and '
                   'comma-separated lists of annotation extensions. Decide if and how '
                   'this should be represented in the schema.',
                   'Annotation extensions do not have a unique identifier, so the '
                   'schema indicates they are inlined as a list. This makes change '
                   'operations that target a specific annotation extension more '
                   'difficult.']} })
    annotation_properties: Optional[list[AnnotationProperty]] = Field(default=None, description="""A list if key-value pairs that provide additional information about a standard
annotation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardAnnotation'],
         'todos': ['Annotation properties do not have a unique identifier, so the '
                   'schema indicates they are inlined as a list. This makes change '
                   'operations that target a specific annotation property more '
                   'difficult.']} })


class AnnotationExtension(ConfiguredBaseModel):
    """
    Annotation extensions allow GO terms in standard annotations to be further
    specified, using gene products, chemicals, cell types, anatomical structures, to
    provide additional biological context.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema'})

    extension_relation: str = Field(default=..., description="""A term from the Relation Ontology that describes how the GO term in the extension
relates to the GO term in the standard annotation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AnnotationExtension']} })
    extension_term: str = Field(default=..., description="""The gene product, chemical, cell type, anatomical structure, or other entity that
is used to further specify the GO term in the standard annotation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AnnotationExtension']} })


class AnnotationProperty(ConfiguredBaseModel):
    """
    A key-value pair that provides additional information about a standard annotation.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema'})

    property_key: str = Field(default=..., description="""The key of an annotation property.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AnnotationProperty']} })
    property_value: str = Field(default=..., description="""The value of an annotation property.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AnnotationProperty']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
StandardAnnotation.model_rebuild()
AnnotationExtension.model_rebuild()
AnnotationProperty.model_rebuild()
