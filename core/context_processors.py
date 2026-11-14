def notifications(request):
    """Expose notification data to the authenticated app shell."""
    if not request.user.is_authenticated:
        return {
            'unread_notifications': 0,
            'recent_notifications': [],
        }

    queryset = request.user.notifications.order_by('-created_at')
    return {
        'unread_notifications': queryset.filter(is_read=False).count(),
        'recent_notifications': list(queryset[:5]),
    }
