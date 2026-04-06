from app.core.permissions import is_admin


def can_view_user(actor, target_user) -> bool:
    return is_admin(actor) or actor.id == target_user.id


def can_edit_user(actor, target_user) -> bool:
    return is_admin(actor) or actor.id == target_user.id


def can_manage_book(actor, book) -> bool:
    return is_admin(actor) or actor.id == book.owner_id


def can_delete_user(actor, target_user) -> bool:
    return is_admin(actor) or actor.id == target_user.id
