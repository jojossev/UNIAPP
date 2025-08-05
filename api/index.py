def handler(event, context):
    try:
        # Réponse minimale pour tester le déploiement
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/plain; charset=utf-8',
                'Access-Control-Allow-Origin': '*'
            },
            'body': 'Bienvenue sur Vercel! La configuration minimale fonctionne!'
        }
    except Exception as e:
        # En cas d'erreur, renvoyer un message d'erreur
        return {
            'statusCode': 500,
            'body': f'Erreur: {str(e)}',
            'isBase64Encoded': False
        }
