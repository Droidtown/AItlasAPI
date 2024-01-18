#!/usr/bin/env python
# -*- coding:utf-8 -*-


Noun = str

from dataclasses import dataclass
from typing import Union

@dataclass
class People:
    person: str

@dataclass
class IntransitiveVerb:
    subj: People
    time: list[str]

@dataclass
class TransitiveVerb:
    obj: Noun
    subj: People
    time: list[str]

@dataclass
class DitransitiveVerb:
    obj01: Noun
    obj02: Noun
    subj: People
    time: list[str]

VerbTypes = Union[IntransitiveVerb, TransitiveVerb, DitransitiveVerb]