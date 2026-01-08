# ------------------------------------------------------------------------------
# Copyright (c) 2026 Phan_Van_Khai
# All rights reserved.
#
# This source code is the proprietary and confidential property of Phan_Van_Khai.
# Unauthorized copying, distribution, or modification of this file, 
# via any medium, is strictly prohibited.
# ------------------------------------------------------------------------------

import sys
def validate_Q (Q_count):
    is_valid = True
    if not Q_count or Q_count < 3:
        is_valid = False
    return is_valid

def validate_F (F_count, Q_count):
    is_valid = True
    if F_count <= 0 or F_count > Q_count:
        is_valid = False
    return is_valid