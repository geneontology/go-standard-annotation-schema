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


metamodel_version = "1.12.0"
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


linkml_meta = None


class Annotation(ConfiguredBaseModel):
    """
    An association between a gene product and a GO term, with an evidence code, a reference to support the association, and other data associated with the gene product or the annotation.
    """
    db_object_id: str = Field(default=..., description="""A unique identifier for the item being annotated.""")
    negation: Optional[bool] = Field(default=None, description="""A boolean indicating whether the annotation is negated.""")
    relation: str = Field(default=..., description="""Relation from the Relation Ontology that describes how the annotated biological entity relates to the GO term with which it is associated.""")
    ontology_class_id: str = Field(default=..., description="""The GO identifier for the term attributed to the DB object ID.""")
    references: list[str] = Field(default=..., description="""One or more unique identifiers for a single source cited as an authority for the attribution of the GO ID to the DB object ID. This may be a literature reference or a database record. Valid references are one of: PubMed, DOI, GO_REF, MOD reference.""", min_length=1)
    evidence_type: str = Field(default=..., description="""The Evidence & Conclusion Ontology (ECO) identifier for the evidence code that supports the association between the DB object ID and the GO term.""")
    with_or_from: Optional[list[str]] = Field(default=None, description="""Used with specific ECO codes to capture an additional identifier supporting the evidence for the annotation. For example, it can identify another gene product to which the annotated gene product is similar (ISS) or interacts with (IPI). Population of the With/From is mandatory for certain evidence codes.""")
    interacting_taxon_id: Optional[list[str]] = Field(default=None, description="""Taxonomic identifier for interacting organism to be used only in conjunction with terms that have the biological process term 'GO:0044419 biological process involved in interspecies interaction between organisms' or the cellular component term 'GO:0018995 host cellular component' as an ancestor. Identifiers must come from NCBI Taxonomy database.""")
    annotation_date: date = Field(default=..., description="""Date on which the annotation was made""")
    assigned_by: str = Field(default=..., description="""The database which made the annotation one of the values from the set of GOC groups; used for tracking the source of an individual annotation.""")
    annotation_extensions: Optional[list[AnnotationExtension]] = Field(default=None, description="""Annotation extensions allow GO terms in annotations to be further specified, using gene products, chemicals, cell types, anatomical structures, to provide additional biological context. The cross-reference is prefaced by an appropriate relationship from the Relation Ontology.""")
    annotation_properties: Optional[AnnotationProperties] = Field(default=None, description="""Additional properties associated with an annotation.""")

    @field_validator('db_object_id')
    def pattern_db_object_id(cls, v):
        pattern=re.compile(r"^(?:[A-Za-z][A-Za-z0-9_\-.]*:[A-Za-z0-9_\-.:/]+)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid db_object_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid db_object_id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('relation')
    def pattern_relation(cls, v):
        pattern=re.compile(r"^(?:[A-Za-z][A-Za-z0-9_\-.]*:[A-Za-z0-9_\-.:/]+)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid relation format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid relation format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('ontology_class_id')
    def pattern_ontology_class_id(cls, v):
        pattern=re.compile(r"^(?:GO:[A-Za-z0-9_\-.:/]+)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid ontology_class_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid ontology_class_id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('references')
    def pattern_references(cls, v):
        pattern=re.compile(r"^(?:[A-Za-z][A-Za-z0-9_\-.]*:[A-Za-z0-9_\-.:/]+)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid references format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid references format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('evidence_type')
    def pattern_evidence_type(cls, v):
        pattern=re.compile(r"^(?:ECO:[A-Za-z0-9_\-.:/]+)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid evidence_type format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid evidence_type format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('with_or_from')
    def pattern_with_or_from(cls, v):
        pattern=re.compile(r"^(?:[A-Za-z][A-Za-z0-9_\-.]*:[A-Za-z0-9_\-.:/]+)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid with_or_from format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid with_or_from format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('interacting_taxon_id')
    def pattern_interacting_taxon_id(cls, v):
        pattern=re.compile(r"^(?:NCBITaxon:[A-Za-z0-9_\-.:/]+)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid interacting_taxon_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid interacting_taxon_id format: {v}"
            raise ValueError(err_msg)
        return v


class AnnotationExtension(ConfiguredBaseModel):
    """
    Annotation extensions allow GO terms in annotations to be further specified, using gene products, chemicals, cell types, anatomical structures, to provide additional biological context.
    """
    extension_relation: str = Field(default=..., description="""A term from the Relation Ontology that describes how the GO term in the extension relates to the GO term in the annotation.""")
    extension_term: str = Field(default=..., description="""The gene product, chemical, cell type, anatomical structure, or other entity that is used to further specify the GO term in the annotation.""")

    @field_validator('extension_relation')
    def pattern_extension_relation(cls, v):
        pattern=re.compile(r"^(?:(RO|BFO):[A-Za-z0-9_\-.:/]+)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid extension_relation format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid extension_relation format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('extension_term')
    def pattern_extension_term(cls, v):
        pattern=re.compile(r"^(?:[A-Za-z][A-Za-z0-9_\-.]*:[A-Za-z0-9_\-.:/]+)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid extension_term format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid extension_term format: {v}"
            raise ValueError(err_msg)
        return v


class AnnotationProperties(ConfiguredBaseModel):
    """
    The closed set of properties associated with an annotation.
    """
    id: Optional[str] = Field(default=None, description="""The contributing database's unique identifier for an annotation.""")
    model_state: Optional[str] = Field(default=None, description="""The GO-CAM model state.""")
    noctua_model_id: Optional[str] = Field(default=None, description="""The unique identifier of the associated GO-CAM model.""")
    contributor_id: Optional[list[str]] = Field(default=None, description="""The identifier of a curator or user who entered or changed an annotation.""")
    reviewer_id: Optional[list[str]] = Field(default=None, description="""The identifier of a curator or user who last reviewed an annotation.""")
    creation_date: Optional[date] = Field(default=None, description="""The date on which the annotation was created.""")
    modification_date: Optional[list[date]] = Field(default=None, description="""A date on which the annotation was modified.""")
    reviewed_date: Optional[list[date]] = Field(default=None, description="""A date on which the annotation was reviewed.""")
    comment: Optional[list[str]] = Field(default=None, description="""Free text about a specific annotation.""")

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^(?:[A-Za-z][A-Za-z0-9_\-.]*:[A-Za-z0-9_\-.:/]+)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('model_state')
    def pattern_model_state(cls, v):
        pattern=re.compile(r"^[A-Za-z_]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid model_state format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid model_state format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('noctua_model_id')
    def pattern_noctua_model_id(cls, v):
        pattern=re.compile(r"^(?:[A-Za-z][A-Za-z0-9_\-.]*:[A-Za-z0-9_\-.:/]+)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid noctua_model_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid noctua_model_id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('contributor_id')
    def pattern_contributor_id(cls, v):
        pattern=re.compile(r"^(?:[A-Za-z][A-Za-z0-9_\-.]*:[A-Za-z0-9_\-.:/]+)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid contributor_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid contributor_id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('reviewer_id')
    def pattern_reviewer_id(cls, v):
        pattern=re.compile(r"^(?:[A-Za-z][A-Za-z0-9_\-.]*:[A-Za-z0-9_\-.:/]+)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid reviewer_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid reviewer_id format: {v}"
            raise ValueError(err_msg)
        return v


class GeneProductProperties(ConfiguredBaseModel):
    """
    The closed set of properties associated with an entity in a GPI row.
    """
    db_subset: Optional[Literal["TrEMBL", "Swiss-Prot"]] = Field(default=None, description="""The status of a UniProtKB accession with respect to curator review.""")
    uniprot_proteome: Optional[str] = Field(default=None, description="""The UniProt proteome accession for the set of proteins that constitute an organism's proteome.""")
    go_annotation_complete: Optional[date] = Field(default=None, description="""The date on which a curator determined that the set of GO annotations for an entity was complete.""")
    go_annotation_summary: Optional[str] = Field(default=None, description="""A textual gene or gene-product description.""")

    @field_validator('uniprot_proteome')
    def pattern_uniprot_proteome(cls, v):
        pattern=re.compile(r"^UP[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid uniprot_proteome format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid uniprot_proteome format: {v}"
            raise ValueError(err_msg)
        return v


class Entity(ConfiguredBaseModel):
    """
    An annotatable biological entity for an organism: protein-coding genes, non-coding RNA genes, protein isoforms (i. e., splice variants) and modified forms, such as cleaved forms or proteins modified by post-translational modifications.
    """
    db_object_id: str = Field(default=..., description="""A unique identifier for the item being annotated.""")
    db_object_symbol: Optional[str] = Field(default=None, description="""The symbol of the entity being annotated.""")
    db_object_name: Optional[str] = Field(default=None, description="""The name of the entity being annotated.""")
    db_object_synonyms: Optional[list[str]] = Field(default=None, description="""Alternative names for the entity being annotated.""")
    db_object_type: str = Field(default=..., description="""The class of biological entity being annotated.""")
    db_object_taxon_id: str = Field(default=..., description="""The NCBI Taxonomy identifier for the organism (species or strain) encoding the entity being annotated.""")
    encoded_by: Optional[list[str]] = Field(default=None, description="""For proteins and transcripts, the gene that encodes the entity being annotated.""")
    canonical_object_id: str = Field(default=..., description="""If the entity being annotated is a gene, gene-centric reference protein or a protein complex, this should repeat the ID of the object being annotated. If the entity being annotated is derived from a gene product such as a protein isoform, a modified protein or a processed transcript (e. g. miRNA), then this refers to the gene-centric ID of the annotated entity.""")
    protein_containing_complex_members: Optional[list[str]] = Field(default=None, description="""If the entity being annotated is a protein-containing complex, this should list the gene-centric canonical protein identifiers.""")
    db_xrefs: Optional[list[str]] = Field(default=None, description="""Cross-references to other databases for the entity being annotated.""")
    gene_product_properties: Optional[GeneProductProperties] = Field(default=None, description="""The properties associated with an entity in a GPI row.""")

    @field_validator('db_object_id')
    def pattern_db_object_id(cls, v):
        pattern=re.compile(r"^(?:[A-Za-z][A-Za-z0-9_\-.]*:[A-Za-z0-9_\-.:/]+)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid db_object_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid db_object_id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('db_object_symbol')
    def pattern_db_object_symbol(cls, v):
        pattern=re.compile(r"^\S+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid db_object_symbol format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid db_object_symbol format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('db_object_type')
    def pattern_db_object_type(cls, v):
        pattern=re.compile(r"^(?:[A-Za-z][A-Za-z0-9_\-.]*:[A-Za-z0-9_\-.:/]+)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid db_object_type format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid db_object_type format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('db_object_taxon_id')
    def pattern_db_object_taxon_id(cls, v):
        pattern=re.compile(r"^(?:NCBITaxon:[A-Za-z0-9_\-.:/]+)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid db_object_taxon_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid db_object_taxon_id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('encoded_by')
    def pattern_encoded_by(cls, v):
        pattern=re.compile(r"^(?:[A-Za-z][A-Za-z0-9_\-.]*:[A-Za-z0-9_\-.:/]+)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid encoded_by format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid encoded_by format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('canonical_object_id')
    def pattern_canonical_object_id(cls, v):
        pattern=re.compile(r"^(?:[A-Za-z][A-Za-z0-9_\-.]*:[A-Za-z0-9_\-.:/]+)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid canonical_object_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid canonical_object_id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('protein_containing_complex_members')
    def pattern_protein_containing_complex_members(cls, v):
        pattern=re.compile(r"^(?:[A-Za-z][A-Za-z0-9_\-.]*:[A-Za-z0-9_\-.:/]+)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid protein_containing_complex_members format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid protein_containing_complex_members format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('db_xrefs')
    def pattern_db_xrefs(cls, v):
        pattern=re.compile(r"^(?:[A-Za-z][A-Za-z0-9_\-.]*:[A-Za-z0-9_\-.:/]+)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid db_xrefs format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid db_xrefs format: {v}"
            raise ValueError(err_msg)
        return v


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Annotation.model_rebuild()
AnnotationExtension.model_rebuild()
AnnotationProperties.model_rebuild()
GeneProductProperties.model_rebuild()
Entity.model_rebuild()
