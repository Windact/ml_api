from marshmallow import Schema, fields
from marshmallow import ValidationError

from api.config import get_logger

_logger = get_logger(logger_name=__name__)

class WaterPumpsSchema(Schema):
    """ Define the input data schema expected by the predict.make_prediction function """

    amount_tsh = fields.Float()
    gps_height = fields.Float()
    construction_year = fields.Int()
    population = fields.Int()
    region =  fields.Str()
    basin =  fields.Str()
    public_meeting =  fields.Boolean(allow_none= True)
    scheme_management =  fields.Str(allow_none = True)
    permit =  fields.Boolean(allow_none = True)
    extraction_type_class =  fields.Str()
    management_group =  fields.Str()
    payment_type =  fields.Str()
    quality_group =  fields.Str()
    quantity_group =  fields.Str()
    source_type =  fields.Str()
    waterpoint_type_group =  fields.Str()


def fitler_errors_from_input_data(data_to_valid,errors):
    """ filter errors from the input data dict list 
    
    Parameters
    ----------
    data_to_valid : list
        A list of dict. It's the input_data that need validation

    errors : dict
        A dictinnary containing Schema.ValidationError error messages. The keys are the indexes in the 
            input_data list of dictinaries and the values are the error messages.
    
    Returns
    -------
    data_to_valid : list
        a list of dictionaries without the dict with Schema.ValidationError
    """

    indexes = errors.keys()

    for idx in indexes:
        del data_to_valid[idx]
    
    return data_to_valid



def validate_data(input_data):
    """ Validate the schema of the input data 
    
    Parameters
    ----------
    input_data : list
        A list of dictionaries with their keys as the columns name and their values as the column's value

    Returns
    -------
    errors : marshmallow.ValidationError
        The catched ValidationError from the Schema.load function
    valid_input : list
        The validated list of cleaned dictionaries
    """

    # Instantiate the schema
    input_data_schema = WaterPumpsSchema(many= True,unknown="EXCLUDE")

    errors = []
    
    try:
        valid_input = input_data_schema.load(input_data)
    except ValidationError as exc:
        errors = exc.messages

    # Extract the dicts with erros from the data
    if len(errors)>0:

        _logger.error(f"Errors in json_data : {errors}")

        no_error_input = fitler_errors_from_input_data(data_to_valid=input_data,errors=errors)
        valid_input = input_data_schema.load(no_error_input)

    return valid_input,errors

