# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 NORDUnet A/S
# All rights reserved.
#
#   Redistribution and use in source and binary forms, with or
#   without modification, are permitted provided that the following
#   conditions are met:
#
#     1. Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#     2. Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided
#        with the distribution.
#     3. Neither the name of the NORDUnet nor the names of its
#        contributors may be used to endorse or promote products derived
#        from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from eduid_userdb.element import Element, VerifiedElement

__author__ = 'lundberg'


@dataclass
class ProofingElement(VerifiedElement):
    """
    Element for holding the state of a proofing flow. It should contain meta data needed for logging
    a proofing according to the Kantara specification.

    Properties of ProofingElement:

        created_by
        created_ts
        is_verified
        verified_by
        verified_ts
        verification_code

    :param data: element parameters from database

    :type data: dict
    """
    verification_code: Optional[str] = None


@dataclass
class _NumberProofingElementRequired:
    """
    """
    number: str


@dataclass
class NinProofingElement(ProofingElement, _NumberProofingElementRequired):
    """
    Element for holding the state of a nin proofing flow.

    Properties of NinProofingElement:

        number
        created_by
        created_ts
        is_verified
        verified_by
        verified_ts
        verification_code

    :param data: element parameters from database

    :type data: dict
    """


@dataclass
class _EmailProofingElementRequired:
    """
    """
    email: str


@dataclass
class EmailProofingElement(ProofingElement, _EmailProofingElementRequired):
    """
    Element for holding the state of an email proofing flow.

    Properties of EmailProofingElement:

        email
        created_by
        created_ts
        is_verified
        verified_by
        verified_ts
        verification_code

    :param data: element parameters from database

    :type data: dict
    """


@dataclass
class PhoneProofingElement(ProofingElement, _NumberProofingElementRequired):
    """
    Element for holding the state of a phone number proofing flow.

    Properties of PhoneProofingElement:

        number
        created_by
        created_ts
        is_verified
        verified_by
        verified_ts
        verification_code

    :param data: element parameters from database

    :type data: dict
    """


@dataclass
class SentLetterElement(Element):
    """
    Properties of SentLetterElement:

    address
    is_sent
    sent_ts
    transaction_id
    created_by
    created_ts
    """
    is_sent: bool = False
    sent_ts: Optional[datetime] = None
    transaction_id: Optional[str] = None
    address: Optional[str] = None
