import pprint

examples = {
    'css': '''
    <style>
    /* Primary color */
    :root {{
        --primary-color: #6F4E37;
    }}

    /* Secondary color */
    :root {{
        --secondary-color: #C9BEB9;
    }}

    /* Accent color */
    :root {{
        --accent-color: #8F7A70;
    }}

    /* Elements */
    body {{
        background-color: #F7F7F7;
        color: #333333;
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: var(--primary-color);
    }}

    a, a:hover, a:focus {{
        color: var(--link-color);
        text-decoration: none;
    }}

    .btn-primary {{
        background-color: var(--primary-color);
        border-color: var(--primary-color);
    }}

    .btn-primary:hover {{
        background-color: #9C7D64;
        border-color: #9C7D64;
    }}

    .btn-primary:focus, .btn-primary:active {{
        background-color: #5F3A1C;
        border-color: #5F3A1C;
    }}

    .btn-secondary {{
        color: var(--primary-color);
        background-color: var(--secondary-color);
        border-color: var(--primary-color);
    }}

    .btn-secondary:hover {{
        background-color: #BDAFA9;
        border-color: var(--primary-color);
    }}

    .btn-secondary:focus, .btn-secondary:active {{
        background-color: #8F7A70;
        border-color: var(--primary-color);
    }}

    .navbar {{
        background-color: var(--primary-color);
    }}

    .navbar-brand {{
        color: var(--secondary-color);
    }}

    .navbar-nav .nav-link {{
        color: var(--secondary-color);
    }}

    .navbar-nav .nav-link:hover, .navbar-nav .nav-link:focus {{
        color: #F0F0F0;
    }}

    .alert-primary {{
        color: var(--primary-color);
        background-color: #F7F7F7;
        border-color: #F7F7F7;
    }}

    .alert-primary hr {{
        border-top-color: #F7F7F7;
    }}

    .alert-primary .alert-link {{
        color: #8F7A70;
    }}

    @media (min-width: 576px) {{
        .navbar-expand-sm .navbar-nav .nav-link {{
            padding-right: 0.5rem;
            padding-left: 0.5rem;
        }}
    }}

    @media (min-width: 768px) {{
        .navbar-expand-md .navbar-nav .nav-link {{
            padding-right: 1rem;
            padding-left: 1rem;
        }}
    }}

    @media (min-width: 992px) {{
        .navbar-expand-lg .navbar-nav .nav-link {{
            padding-right: 1.5rem;
            padding-left: 1.5rem;
        }}
    }}

    @media (min-width: 1200px) {{
        .navbar-expand-xl .navbar-nav .nav-link {{
            padding-right: 2rem;
            padding-left: 2rem;
        }}
    }}
    </style>
    ''',
    'scaffold': '''
    <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{website_title}</title>
            
            <!-- Bootstrap CSS & JS -->
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
            
            <!-- Font Awesome CSS -->
            <link href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet">
            
        </head>
        </html>
    ''',
    'navbar': '''
    <nav class="navbar navbar-expand-sm navbar-dark bg-dark" aria-label="Third navbar example">
            <div class="container-fluid">
                <a class="navbar-brand" href="#">Expand at sm</a>
                <button class="navbar-toggler collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#navbarsExample03" aria-controls="navbarsExample03" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>

                <div class="navbar-collapse collapse" id="navbarsExample03" style="">
                    <ul class="navbar-nav me-auto mb-2 mb-sm-0">
                        <li class="nav-item">
                            <a class="nav-link active" aria-current="page" href="#">Home</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#">Link</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link disabled" href="#" tabindex="-1" aria-disabled="true">Disabled</a>
                        </li>
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" id="dropdown03" data-bs-toggle="dropdown" aria-expanded="false">Dropdown</a>
                            <ul class="dropdown-menu" aria-labelledby="dropdown03">
                                <li><a class="dropdown-item" href="#">Action</a></li>
                                <li><a class="dropdown-item" href="#">Another action</a></li>
                                <li><a class="dropdown-item" href="#">Something else here</a></li>
                            </ul>
                        </li>
                    </ul>
                    <form>
                        <input class="form-control" type="text" placeholder="Search" aria-label="Search">
                    </form>
                </div>
            </div>
        </nav>
    ''',
}