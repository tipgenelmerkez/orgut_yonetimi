def update_followers(record, old_members=set(), new_members=set()):
    if not old_members:
        old_members = set(record.member_line_ids.ids)
    if not new_members:
        new_members = set(record.member_line_ids.ids)

    removed_members = old_members - new_members
    added_members = new_members - old_members

    if removed_members:
        record.message_unsubscribe(partner_ids=list(removed_members))
    if added_members:
        record.message_subscribe(partner_ids=list(added_members))
