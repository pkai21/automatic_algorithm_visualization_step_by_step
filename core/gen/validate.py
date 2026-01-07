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