2003:f3:4f1a:af00:f975:3e59:f622:dbbf,172.18.0.1 - - [16/Apr/2025 21:38:52] "OPTIONS /saveMessage HTTP/1.1" 200 402 0.005617

Traceback (most recent call last):

  File "/usr/local/lib/python3.12/site-packages/flask/app.py", line 2532, in wsgi_app

    response = self.handle_exception(e)

               ^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.12/site-packages/flask_cors/extension.py", line 194, in wrapped_function

    return cors_after_request(app.make_response(f(*args, **kwargs)))

                                                ^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.12/site-packages/flask/app.py", line 2529, in wsgi_app

    response = self.full_dispatch_request()

               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.12/site-packages/flask/app.py", line 1825, in full_dispatch_request

    rv = self.handle_user_exception(e)

         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.12/site-packages/flask_cors/extension.py", line 194, in wrapped_function

    return cors_after_request(app.make_response(f(*args, **kwargs)))

                                                ^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.12/site-packages/flask/app.py", line 1823, in full_dispatch_request

    rv = self.dispatch_request()

         ^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.12/site-packages/flask/app.py", line 1799, in dispatch_request

    return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.12/site-packages/flask_jwt_extended/view_decorators.py", line 170, in decorator

    return current_app.ensure_sync(fn)(*args, **kwargs)

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/src/app/api/routes.py", line 130, in save_message

    is_group = data.get("isGroup", "false").lower() == "true"  # Default to False if not provided

               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

AttributeError: 'bool' object has no attribute 'lower'