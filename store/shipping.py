from decimal import Decimal

import easypost
from django.conf import settings


class ShippingQuoteError(Exception):
    pass


def _build_origin_address():
    return {
        'name': settings.EASYPOST_ORIGIN_NAME,
        'street1': settings.EASYPOST_ORIGIN_STREET1,
        'street2': settings.EASYPOST_ORIGIN_STREET2,
        'city': settings.EASYPOST_ORIGIN_CITY,
        'state': settings.EASYPOST_ORIGIN_STATE,
        'zip': settings.EASYPOST_ORIGIN_ZIP,
        'country': settings.EASYPOST_ORIGIN_COUNTRY,
    }


def _build_default_parcel():
    return {
        'length': str(settings.EASYPOST_PARCEL_LENGTH_IN),
        'width': str(settings.EASYPOST_PARCEL_WIDTH_IN),
        'height': str(settings.EASYPOST_PARCEL_HEIGHT_IN),
        'weight': str(settings.EASYPOST_PARCEL_WEIGHT_OZ),
    }


def get_usps_shipping_quote(to_address):
    if not settings.EASYPOST_API_KEY:
        raise ShippingQuoteError('Shipping is not configured. Set EASYPOST_API_KEY to continue.')

    try:
        client = easypost.EasyPostClient(settings.EASYPOST_API_KEY)
        shipment = client.shipment.create(
            to_address=to_address,
            from_address=_build_origin_address(),
            parcel=_build_default_parcel(),
        )
    except Exception as exc:
        raise ShippingQuoteError('Unable to fetch USPS shipping rates right now.') from exc

    usps_rates = [rate for rate in shipment.rates if getattr(rate, 'carrier', '') == 'USPS']
    if not usps_rates:
        raise ShippingQuoteError('No USPS shipping rates are available for this address.')

    best_rate = min(usps_rates, key=lambda rate: Decimal(str(rate.rate)))

    return {
        'carrier': best_rate.carrier,
        'service': best_rate.service,
        'amount': Decimal(str(best_rate.rate)),
        'currency': best_rate.currency,
    }
