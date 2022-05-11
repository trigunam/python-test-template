
class InputValidator:
    """Validate the mandatory keys and skip the optional keys using the validator.
    Usage:
    InputValidator(config, [mandatory_keys], [optional_keys]).validate_required_inputs()

    Return true if all the mandatory keys are present in the config.
    If one of them is not present or empty, a ValueError is thrown with "Invalid input, key_name"
    """
    def __init__(self, config, mandatory_keys, optional_keys=None):
        super(InputValidator, self).__init__()
        self.config = config
        self.mandatory_keys = mandatory_keys
        self.optional_keys = optional_keys

    def valid_input(self, key):
        if key not in self.config or not self.config[key].strip():
            err_msg = 'Invalid input, {}'.format(key)
            print(err_msg)
            raise ValueError(err_msg)
        return True

    def validate_required_inputs(self):
        is_valid_input = False
        for key in self.mandatory_keys:
            is_valid_input = self.valid_input(key)
            if not is_valid_input:
                break

        return is_valid_input


if __name__ == '__main__':
    print(InputValidator({
        'username': 'a',
        'password': 'a',
        'client_id': 'a',
        'client_secret': 'a',
        'iam_url': 'a',
        'idm_url': 'a',
        'token_api_version': 'a',
        'client_api_version': 'a'
    }, ['username', 'password',
        'client_id', 'client_secret',
        'iam_url', 'idm_url',
        'token_api_version', 'client_api_version'
        ]).validate_required_inputs())
