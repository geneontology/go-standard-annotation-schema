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
     'notes': ['This schema uses custom types with structured patterns to '
               'represent various types of identifiers. However, LinkML tooling '
               'currently does not materialize structured patterns in generated '
               'artifacts. The necessary changes are currently (as of 2026-08-13) '
               'pending in https://github.com/linkml/linkml/pull/3832. Once this '
               'PR is merged, the changes released, and the LinkML dependency in '
               'this project updated, we will have stronger validation of '
               'identifier formats.',
               'This schema deviates from the grammar and specs when necessary to '
               'either reflect actual data or to establish better modeling '
               'practices. These deviations are documented as notes on specific '
               'schema elements.'],
     'prefixes': {'GO': {'prefix_prefix': 'GO',
                         'prefix_reference': 'http://purl.obolibrary.org/obo/GO_'},
                  'PR': {'prefix_prefix': 'PR',
                         'prefix_reference': 'http://purl.obolibrary.org/obo/PR_'},
                  'SO': {'prefix_prefix': 'SO',
                         'prefix_reference': 'http://purl.obolibrary.org/obo/SO_'},
                  'go_standard_annotation_schema': {'prefix_prefix': 'go_standard_annotation_schema',
                                                    'prefix_reference': 'https://w3id.org/geneontology/go-standard-annotation-schema/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'schema': {'prefix_prefix': 'schema',
                             'prefix_reference': 'http://schema.org/'},
                  'shex': {'prefix_prefix': 'shex',
                           'prefix_reference': 'http://www.w3.org/ns/shex#'},
                  'xsd': {'prefix_prefix': 'xsd',
                          'prefix_reference': 'http://www.w3.org/2001/XMLSchema#'}},
     'see_also': ['https://geneontology.github.io/go-standard-annotation-schema',
                  'https://github.com/geneontology/go-annotation/blob/master/specs/gpad-gpi-2-0.md',
                  'https://geneontology.github.io/docs/gene-product-association-data-gpad-format',
                  'https://geneontology.org/docs/gene-product-information-gpi-format-2.0'],
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
               'contributor_identifier': {'description': 'An identifier of a '
                                                         'contributor, such as a '
                                                         'curator or user who '
                                                         'entered or changed an '
                                                         'annotation.',
                                          'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                                          'name': 'contributor_identifier',
                                          'notes': ['The GPAD/GPI grammar says '
                                                    'that this type of identifier '
                                                    'must have an orcid or goc '
                                                    'prefix. In practice a full '
                                                    'https://orcid.org URL is '
                                                    'used. For now, this schema is '
                                                    'not enforcing a specific '
                                                    'prefix.'],
                                          'typeof': 'external_identifier'},
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
                                                      'such as a gene product, an '
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
               'ro_identifier': {'description': 'An identifier of a Relation '
                                                'Ontology term.',
                                 'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
                                 'name': 'ro_identifier',
                                 'structured_pattern': {'interpolated': True,
                                                        'partial_match': False,
                                                        'syntax': '(RO|BFO):{local_id}'},
                                 'typeof': 'external_identifier'},
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


class Annotation(ConfiguredBaseModel):
    """
    An association between a gene product and a GO term, with an evidence code, a reference to support the association, and other data associated with the gene product or the annotation.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema'})

    db_object_id: str = Field(default=..., description="""A unique identifier for the item being annotated.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Annotation', 'Entity']} })
    negation: Optional[bool] = Field(default=None, description="""A boolean indicating whether the annotation is negated.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Annotation'],
         'notes': ['Decide if this should be required in the schema so that it is '
                   'always explicitly set to true or false. Or, is it okay to have it '
                   'be optional and assumed false if not present?']} })
    relation: str = Field(default=..., description="""Relation from the Relation Ontology that describe how the annotated biological entity relates to the GO term with which it is associated.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Annotation'],
         'notes': ['The GPAD spec says that the "relation used SHOULD come from the '
                   'allowed gene-product-to-term relations". Decide whether to enforce '
                   'this in the schema via an enum.']} })
    ontology_class_id: str = Field(default=..., description="""The GO identifier for the term attributed to the DB object ID.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Annotation']} })
    references: list[str] = Field(default=..., description="""One or more unique identifiers for a single source cited as an authority for the attribution of the GO ID to the DB object ID. This may be a literature reference or a database record. Valid references are one of: PubMed, DOI, GO_REF, MOD reference.""", min_length=1, json_schema_extra = { "linkml_meta": {'domain_of': ['Annotation']} })
    evidence_type: str = Field(default=..., description="""The Evidence & Conclusion Ontology (ECO) identifier for the evidence code that supports the association between the DB object ID and the GO term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Annotation']} })
    with_or_from: Optional[list[str]] = Field(default=None, description="""Used with specific ECO codes to capture an additional identifier supporting the evidence for the annotation. For example, it can identify another gene product to which the annotated gene product is similar (ISS) or interacts with (IPI). Population of the With/From is mandatory for certain evidence codes.""", json_schema_extra = { "linkml_meta": {'comments': ['Cardinality must be 0 for evidence codes IDA, TAS, NAS, or ND',
                      'Cardinality must be 1, >1 for IEA, IC, IGI, IPI, ISS & child '
                      'terms of ISS'],
         'domain_of': ['Annotation']} })
    interacting_taxon_id: Optional[list[str]] = Field(default=None, description="""Taxonomic identifier for interacting organism to be used only in conjunction with terms that have the biological process term 'GO:0044419 biological process involved in interspecies interaction between organisms' or the cellular component term 'GO:0018995 host cellular component' as an ancestor. Identifiers must come from NCBI Taxonomy database.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Annotation']} })
    annotation_date: date = Field(default=..., description="""Date on which the annotation was made""", json_schema_extra = { "linkml_meta": {'domain_of': ['Annotation'],
         'notes': ['The GPAD file description says that this is a date in the format '
                   '`YYYY-MM-DD`. The spec says that it is a date or datetime. Decide '
                   'whether to permit date, datetime, or both.']} })
    assigned_by: str = Field(default=..., description="""The database which made the annotation one of the values from the set of GOC groups; used for tracking the source of an individual annotation.""", json_schema_extra = { "linkml_meta": {'comments': ['Value may differ from the DB:DB Object ID column. Any '
                      'annotation that is made by one database and incorporated into '
                      'another retains the original value.'],
         'domain_of': ['Annotation']} })
    annotation_extensions: Optional[list[AnnotationExtension]] = Field(default=None, description="""Annotation extensions allow GO terms in annotations to be further specified, using gene products, chemicals, cell types, anatomical structures, to provide additional biological context. The cross-reference is prefaced by an appropriate relationship from the Relation Ontology.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Annotation'],
         'notes': ['Annotation extensions do not have a unique identifier, so the '
                   'schema indicates they are inlined as a list. This makes change '
                   'operations that target a specific annotation extension more '
                   'difficult.']} })
    annotation_properties: Optional[AnnotationProperties] = Field(default=None, description="""Additional properties associated with an annotation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Annotation']} })


class AnnotationExtension(ConfiguredBaseModel):
    """
    Annotation extensions allow GO terms in annotations to be further specified, using gene products, chemicals, cell types, anatomical structures, to provide additional biological context.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema'})

    extension_relation: str = Field(default=..., description="""A term from the Relation Ontology that describes how the GO term in the extension relates to the GO term in the annotation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AnnotationExtension']} })
    extension_term: str = Field(default=..., description="""The gene product, chemical, cell type, anatomical structure, or other entity that is used to further specify the GO term in the annotation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AnnotationExtension']} })


class AnnotationProperties(ConfiguredBaseModel):
    """
    The closed set of properties associated with an annotation.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
         'notes': ['Attributes are used instead of slots here because the names of the '
                   'attributes are somewhat tightly coupled to the GPAD file format. '
                   'They should not be reused or modified in other contexts, as '
                   'top-level slots might be.']})

    id: Optional[str] = Field(default=None, description="""The contributing database's unique identifier for an annotation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AnnotationProperties']} })
    model_state: Optional[str] = Field(default=None, description="""The GO-CAM model state.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AnnotationProperties'],
         'notes': ['The GPAD grammar says that this should be a string of only '
                   "alphabetic characters, but this doesn't account for the already "
                   'used "internal_test" model state. The pattern has been updated to '
                   'allow underscores as well.']} })
    noctua_model_id: Optional[str] = Field(default=None, description="""The unique identifier of the associated GO-CAM model.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AnnotationProperties']} })
    contributor_id: Optional[list[str]] = Field(default=None, description="""The identifier of a curator or user who entered or changed an annotation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AnnotationProperties']} })
    reviewer_id: Optional[list[str]] = Field(default=None, description="""The identifier of a curator or user who last reviewed an annotation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AnnotationProperties']} })
    creation_date: Optional[date] = Field(default=None, description="""The date on which the annotation was created.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AnnotationProperties'],
         'notes': ['The grammar says this should be a date or datetime, but the '
                   'narrative spec is less clear. This is being modeled as a date to '
                   'keep it in alignment with other date fields for now.']} })
    modification_date: Optional[list[date]] = Field(default=None, description="""A date on which the annotation was modified.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AnnotationProperties'],
         'notes': ['The grammar says this should be a date or datetime, but the '
                   'narrative spec is less clear. This is being modeled as a date to '
                   'keep it in alignment with other date fields for now.']} })
    reviewed_date: Optional[list[date]] = Field(default=None, description="""A date on which the annotation was reviewed.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AnnotationProperties'],
         'notes': ['The grammar says this should be a date or datetime, but the '
                   'narrative spec is less clear. This is being modeled as a date to '
                   'keep it in alignment with other date fields for now.']} })
    comment: Optional[list[str]] = Field(default=None, description="""Free text about a specific annotation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AnnotationProperties']} })

    @field_validator('model_state')
    def pattern_model_state(cls, v):
        pattern=re.compile(r"^[A-Za-z_]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid model_state format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid model_state format: {v}"
            raise ValueError(err_msg)
        return v


class GeneProductProperties(ConfiguredBaseModel):
    """
    The closed set of properties associated with an entity in a GPI row.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema',
         'notes': ['Attributes are used instead of slots here because the names of the '
                   'attributes are somewhat tightly coupled to the GPI file format. '
                   'They should not be reused or modified in other contexts, as '
                   'top-level slots might be.']})

    db_subset: Optional[Literal["TrEMBL", "Swiss-Prot"]] = Field(default=None, description="""The status of a UniProtKB accession with respect to curator review.""", json_schema_extra = { "linkml_meta": {'domain_of': ['GeneProductProperties'],
         'equals_string_in': ['TrEMBL', 'Swiss-Prot'],
         'notes': ['Using equals_string_in instead of an enum here to avoid issues '
                   'with the specific capitalization and punctuation of the values.']} })
    uniprot_proteome: Optional[str] = Field(default=None, description="""The UniProt proteome accession for the set of proteins that constitute an organism's proteome.""", json_schema_extra = { "linkml_meta": {'domain_of': ['GeneProductProperties'],
         'notes': ['The GPI grammar says this should be a prefixed identifier, but the '
                   'example shows an unprefixed identifier. It is unclear what is '
                   'actually used in practice. This is being modeled as an unprefixed '
                   'identifier for now.']} })
    go_annotation_complete: Optional[date] = Field(default=None, description="""The date on which a curator determined that the set of GO annotations for an entity was complete.""", json_schema_extra = { "linkml_meta": {'domain_of': ['GeneProductProperties'],
         'notes': ['The GPI grammar and spec say this can be a date or datetime. It is '
                   'unclear what is actually used in practice. This is being modeled '
                   'as a date to keep it in alignment with other date fields for now.']} })
    go_annotation_summary: Optional[str] = Field(default=None, description="""A textual gene or gene-product description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['GeneProductProperties']} })

    @field_validator('uniprot_proteome')
    def pattern_uniprot_proteome(cls, v):
        pattern=re.compile(r"^UP[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid uniprot_proteome format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid uniprot_proteome format: {v}"
            raise ValueError(err_msg)
        return v


class Entity(ConfiguredBaseModel):
    """
    An annotatable biological entity for an organism: protein-coding genes, non-coding RNA genes, protein isoforms (i. e., splice variants) and modified forms, such as cleaved forms or proteins modified by post-translational modifications.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/geneontology/go-standard-annotation-schema'})

    db_object_id: str = Field(default=..., description="""A unique identifier for the item being annotated.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Annotation', 'Entity']} })
    db_object_symbol: Optional[str] = Field(default=None, description="""The symbol of the entity being annotated.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Entity'],
         'notes': ['The GPI grammar and narrative spec both say that this is required, '
                   'but in practice it is missing in many rows of existing GPI files. '
                   'Decide whether this should be required in the schema and handled '
                   'in the file parsing code if it is missing.']} })
    db_object_name: Optional[str] = Field(default=None, description="""The name of the entity being annotated.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Entity'],
         'notes': ['The GPI grammar implies that column 3 is required, but the '
                   'narrative spec says that it is optional. The narrative spec seems '
                   'more appropriate, so that is what is implemented here. Decide if '
                   'that is correct.']} })
    db_object_synonyms: Optional[list[str]] = Field(default=None, description="""Alternative names for the entity being annotated.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Entity']} })
    db_object_type: str = Field(default=..., description="""The class of biological entity being annotated.""", json_schema_extra = { "linkml_meta": {'comments': ['This field should describe the type of biological object as '
                      'defined by the contributing database. For example, WormBase '
                      'identifiers represent genes, PomBase identifiers represent '
                      'protein-coding genes, and SGD identifiers represent proteins.',
                      'The entity type value must be provided as an ontology term '
                      'identifier from Sequence Ontology, Protein Ontology, or GO, and '
                      'must correspond to one of the permitted GPI entity types or a '
                      'more granular child term. Common entries include PR:000000001 '
                      '(protein), GO:0032991 (protein-containing complex), SO:0001217 '
                      '(protein-coding gene), SO:0000655 (ncRNA) or any SO child term, '
                      'SO:0001263 (ncRNA-coding gene) or any SO child term, SO:0000336 '
                      '(pseudogene).',
                      "GO does not allow 'gene' and 'gene product' as biological "
                      'entity types, as this does not allow to differentiate between '
                      'proteins and ncRNAs products.'],
         'domain_of': ['Entity'],
         'notes': ["The GPI grammar says that column 5 has cardinality 1..*, `ID ( '|' "
                   'ID )*` but the narrative spec says that it cardinality 1. The '
                   'narrative spec seems more appropriate, so that is what is '
                   'implemented here. Decide if that is correct.']} })
    db_object_taxon_id: str = Field(default=..., description="""The NCBI Taxonomy identifier for the organism (species or strain) encoding the entity being annotated.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Entity']} })
    encoded_by: Optional[list[str]] = Field(default=None, description="""For proteins and transcripts, the gene that encodes the entity being annotated.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Entity']} })
    canonical_object_id: str = Field(default=..., description="""If the entity being annotated is a gene, gene-centric reference protein or a protein complex, this should repeat the ID of the object being annotated. If the entity being annotated is derived from a gene product such as a protein isoform, a modified protein or a processed transcript (e. g. miRNA), then this refers to the gene-centric ID of the annotated entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Entity'],
         'notes': ['The GPI grammar says that column 8 has cardinality 0..*, `( ID ( '
                   "'|' ID )* )?` but the narrative spec says that it cardinality 1. "
                   'The narrative spec seems more appropriate, so that is what is '
                   'implemented here. Decide if that is correct.']} })
    protein_containing_complex_members: Optional[list[str]] = Field(default=None, description="""If the entity being annotated is a protein-containing complex, this should list the gene-centric canonical protein identifiers.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Entity']} })
    db_xrefs: Optional[list[str]] = Field(default=None, description="""Cross-references to other databases for the entity being annotated.""", json_schema_extra = { "linkml_meta": {'comments': ["This field is mandatory if the prefix of the annotated entity's "
                      'identifier is not UniProtKB, RNACentral, or ComplexPortal. In '
                      'these cases, db_xrefs must include the corresponding UniProtKB '
                      'ID, RNACentral, or ComplexPortal as appropriate according to '
                      'the Object Type.',
                      'Additional cross references such as NCBI gene or protein IDs, '
                      'HGNC, etc, may also be included.'],
         'domain_of': ['Entity']} })
    gene_product_properties: Optional[GeneProductProperties] = Field(default=None, description="""The properties associated with an entity in a GPI row.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Entity']} })

    @field_validator('db_object_symbol')
    def pattern_db_object_symbol(cls, v):
        pattern=re.compile(r"^\S+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid db_object_symbol format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid db_object_symbol format: {v}"
            raise ValueError(err_msg)
        return v


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Annotation.model_rebuild()
AnnotationExtension.model_rebuild()
AnnotationProperties.model_rebuild()
GeneProductProperties.model_rebuild()
Entity.model_rebuild()
