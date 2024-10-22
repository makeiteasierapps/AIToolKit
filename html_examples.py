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
            <title>Basic Web Page</title>
            
            <!-- Bootstrap CSS & JS -->
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-KK94CHFLLe+nY2dmCWGMq91rCGa5gtU4mk92HdvYe+M/SXH301p5ILy+dN9+nJOZ" crossorigin="anonymous">
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ENjdO4Dr2bkBIFxQpeoTz1HIcje39Wm4jDKdf19U8gI4ddQ3GYNS7NTKfAdVQSZe" crossorigin="anonymous"></script>
            
            <!-- Font Awesome CSS -->
            <link href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet">
            
            <!-- Custom styles -->
            <style>
            
            </style>
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
    'body': [{'Business Example 1': '''<main class="flex-shrink-0">
            <!-- Home Section-->
            <section class="bg-light py-5">
                <div class="container px-5">
                    <div class="row gx-5 justify-content-center">
                        <div class="col-lg-10 col-xl-8">
                            <div class="text-center">
                                <h1 class="display-4 fw-bolder mb-5">Welcome to our eco-friendly bed and breakfast</h1>
                                <p class="lead fw-light mb-5">Experience a serene and sustainable stay with us</p>
                                <a class="btn btn-primary btn-lg px-4" href="#rooms-rates">Explore Rooms &amp; Rates</a>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            <!-- Rooms and Rates Section-->
            <section class="py-5" id="rooms-rates">
                <div class="container px-5">
                    <div class="row gx-5">
                        <div class="col-lg-4 mb-5">
                            <div class="card h-100 border-0 shadow">
                                <img class="card-img-top" src="https://source.unsplash.com/900x600/?bedroom" alt="...">
                                <div class="card-body p-4">
                                    <h5 class="card-title mb-0">Standard Room</h5>
                                    <div class="small text-muted mb-3">Starting at $120/night</div>
                                    <p class="card-text">Our standard room offers a comfortable queen-size bed and a private bathroom. Enjoy the view of our garden and the fresh air from our eco-friendly windows.</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-lg-4 mb-5">
                            <div class="card h-100 border-0 shadow">
                                <img class="card-img-top" src="https://source.unsplash.com/900x600/?suite" alt="...">
                                <div class="card-body p-4">
                                    <h5 class="card-title mb-0">Suite</h5>
                                    <div class="small text-muted mb-3">Starting at $200/night</div>
                                    <p class="card-text">Indulge in our spacious suite, featuring a king-size bed, a private balcony, and a luxurious bathroom with a Jacuzzi. Perfect for a romantic getaway or a special occasion.</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-lg-4 mb-5">
                            <div class="card h-100 border-0 shadow">
                                <img class="card-img-top" src="https://source.unsplash.com/900x600/?cottage" alt="...">
                                <div class="card-body p-4">
                                    <h5 class="card-title mb-0">Cottage</h5>
                                    <div class="small text-muted mb-3">Starting at $300/night</div>
                                    <p class="card-text">Experience the ultimate privacy and comfort in our cozy cottage, nestled in the heart of our garden. Enjoy a fully equipped kitchen, a fireplace, and a private patio. Perfect for a family or a group of friends.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            <!-- About Us Section-->
            <section class="py-5">
                <div class="container px-5">
                    <div class="row gx-5 align-items-center">
                        <div class="col-lg-6">
                            <div class="p-5"><img class="img-fluid rounded-circle" src="https://source.unsplash.com/900x600/?portrait" alt="..."></div>
                        </div>
                        <div class="col-lg-6">
                            <div class="p-5">
                                <h2 class="display-4 fw-bold">About Us</h2>
                                <p class="lead fw-light">We are a family-owned bed and breakfast committed to sustainability and hospitality.</p>
                                <p class="text-muted">Our story began with a passion for nature and a dream of creating a cozy and eco-friendly retreat for travelers. We built our bed and breakfast with locally sourced materials and sustainable practices, such as solar panels, rainwater harvesting, and composting. We strive to provide our guests with a serene and memorable experience, from our organic breakfast to our comfortable rooms and personalized service. Don't just take our word for it, read what our satisfied guests have to say:</p>
                                <blockquote class="blockquote">
                                    <p class="mb-0">"I had the most wonderful stay at this bed and breakfast. The room was cozy and clean, and the breakfast was delicious. But what really stood out was the attention to detail and the personal touch. The owners are lovely people who truly care about their guests and the environment. I can't wait to come back!"</p>
                                    <footer class="blockquote-footer">Alice, <cite title="Source Title">San Francisco, CA</cite></footer>
                                </blockquote>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            <!-- Contact Us Section-->
            <section class="bg-light py-5">
                <div class="container px-5">
                    <div class="row gx-5 justify-content-center">
                        <div class="col-lg-8 col-xl-6">
                            <div class="text-center mb-5">
                                <h2 class="display-4 fw-bold">Contact Us</h2>
                                <p class="lead fw-light mb-0">We'd love to hear from you</p>
                            </div>
                            <form>
                                <div class="form-floating mb-3">
                                    <input class="form-control" id="inputName" type="text" placeholder="Enter your name...">
                                    <label for="inputName">Name</label>
                                </div>
                                <div class="form-floating mb-3">
                                    <input class="form-control" id="inputEmail" type="email" placeholder="Enter your email...">
                                    <label for="inputEmail">Email address</label>
                                </div>
                                <div class="form-floating mb-3">
                                    <textarea class="form-control" id="inputMessage" placeholder="Enter your message here..." style="height: 10rem"></textarea>
                                    <label for="inputMessage">Message</label>
                                </div>
                                <div class="d-grid"><button class="btn btn-primary btn-lg" type="submit">Submit</button></div>
                            </form>
                        </div>
                    </div>
                </div>
            </section>
        </main>
        <!-- Footer-->
        <footer class="bg-light py-4 mt-auto">
            <div class="container px-5">
                <div class="row align-items-center justify-content-between flex-column flex-sm-row">
                    <div class="col-auto"><div class="small m-0">© 2021 Eco-friendly Bed and Breakfast. All rights reserved.</div></div>
                    <div class="col-auto">
                        <a class="small" href="#!">Privacy Policy</a>
                        <span class="mx-1">·</span>
                        <a class="small" href="#!">Terms of Use</a>
                        <span class="mx-1">·</span>
                        <a class="small" href="#!">Contact Us</a>
                    </div>
                </div>
            </div>
        </footer>
    </div>
</body>'''},
        {'Portfolio Example 4': '''
        <body>        
        <main class="flex-shrink-0">
            <!-- Header-->
            <header class="py-5">
                <div class="container px-5 pb-5">
                    <div class="row gx-5 align-items-center">
                        <div class="col-xxl-5">
                            <!-- Header text content-->
                            <div class="text-center text-xxl-start">
                                <div class="badge bg-gradient-primary-to-secondary text-white mb-4"><div class="text-uppercase">Web Development · Design · Marketing</div></div>
                                <div class="fs-3 fw-light text-muted">Welcome to my portfolio</div>
                                <h1 class="display-3 fw-bolder mb-5"><span class="text-gradient d-inline">See my work and let's create something amazing together</span></h1>
                                <div class="d-grid gap-3 d-sm-flex justify-content-sm-center justify-content-xxl-start mb-3">
                                    <a class="btn btn-primary btn-lg px-5 py-3 me-sm-3 fs-6 fw-bolder" href="#contact">Contact Me</a>
                                    <a class="btn btn-outline-dark btn-lg px-5 py-3 fs-6 fw-bolder" href="#projects">View Projects</a>
                                </div>
                            </div>
                        </div>
                        <div class="col-xxl-7">
                            <!-- Header profile picture-->
                            <div class="d-flex justify-content-center mt-5 mt-xxl-0">
                                <div class="profile bg-gradient-primary-to-secondary">
                                    <!-- TIP: For best results, use a photo with a transparent background like the demo example below-->
                                    <!-- Watch a tutorial on how to do this on YouTube (link)-->
                                    <img class="profile-img" src="https://source.unsplash.com/900x600/?portfolio" alt="Portfolio">
                                    <div class="dots-1">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div></header>
            <!-- About Section-->
            <section class="bg-light py-5">
                <div class="container px-5">
                    <div class="row gx-5 justify-content-center">
                        <div class="col-xxl-8">
                            <div class="text-center my-5">
                                <h2 class="display-5 fw-bolder"><span class="text-gradient d-inline">About Me</span></h2>
                                <p class="lead fw-light mb-4">My name is John Doe and I am a full-stack web developer.</p>
                                <p class="text-muted">I specialize in creating beautiful, responsive websites and web applications that are tailored to meet your specific needs. With a strong focus on user experience, I am dedicated to delivering high-quality work that exceeds your expectations.</p>
                                <div class="d-flex justify-content-center fs-2 gap-4">
                                    <a class="text-gradient" href="#!"><i class="bi bi-twitter"></i></a>
                                    <a class="text-gradient" href="#!"><i class="bi bi-linkedin"></i></a>
                                    <a class="text-gradient" href="#!"><i class="bi bi-github"></i></a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            <!-- Skills Section -->
            <section id="skills" class="bg-secondary py-5">
                <div class="container">
                <h2 class="fw-bold mb-4">Skills</h2>
                <div class="row gx-5">
                    <div class="col-lg-4 mb-5">
                    <div class="card h-100 border-0 shadow">
                        <div class="card-body">
                        <i class="bi bi-code-slash display-1 mb-3"></i>
                        <h5 class="card-title fw-bold mb-3">Programming</h5>
                        <p class="card-text">Brief description of programming skill. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed blandit, nisl ac hendrerit mattis, nulla mauris bibendum nisl, vel luctus dolor libero vel velit.</p>
                        </div>
                    </div>
                    </div>
                    <div class="col-lg-4 mb-5">
                    <div class="card h-100 border-0 shadow">
                        <div class="card-body">
                        <i class="bi bi-brush display-1 mb-3"></i>
                        <h5 class="card-title fw-bold mb-3">Design</h5>
                        <p class="card-text">Brief description of design skill. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed blandit, nisl ac hendrerit mattis, nulla mauris bibendum nisl, vel luctus dolor libero vel velit.</p>
                        </div>
                    </div>
                    </div>
                    <div class="col-lg-4 mb-5">
                    <div class="card h-100 border-0 shadow">
                        <div class="card-body">
                        <i class="bi bi-camera2 display-1 mb-3"></i>
                        <h5 class="card-title fw-bold mb-3">Photography</h5>
                        <p class="card-text">Brief description of photography skill. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed blandit, nisl ac hendrerit mattis, nulla mauris bibendum nisl, vel luctus dolor libero vel velit.</p>
                        </div>
                    </div>
                    </div>
                </div>
                </div>
            </section>
            <!-- Projects Section-->
            <section class="py-5" id="projects">
                <div class="container px-5 my-5">
                    <div class="text-center">
                        <h2 class="display-5 fw-bolder"><span class="text-gradient d-inline">My Projects</span></h2>
                    </div>
                    <div class="row gx-5 justify-content-center">
                        <div class="col-lg-4 col-md-6 mb-5">
                            <div class="card">
                                <img class="card-img-top" src="https://source.unsplash.com/500x300/?web development" alt="Web Development Project">
                                <div class="card-body">
                                    <h5 class="card-title fw-bold mb-3">Web Development Project</h5>
                                    <p class="card-text">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin accumsan lacus non neque vehicula, ac blandit tortor tempor. Duis quis felis vel enim finibus commodo at et nisi. Nam lacinia, quam ac bibendum molestie, tellus augue tincidunt risus, vel bibendum nisi velit euismod nunc.</p>
                                    <a href="#" class="btn btn-primary mt-3">View Project</a>
                                </div>
                            </div>
                        </div>
                        <div class="col-lg-4 col-md-6 mb-5">
                            <div class="card">
                                <img class="card-img-top" src="https://source.unsplash.com/500x300/?design" alt="Design Project">
                                <div class="card-body">
                                    <h5 class="card-title fw-bold mb-3">Design Project</h5>
                                    <p class="card-text">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin accumsan lacus non neque vehicula, ac blandit tortor tempor. Duis quis felis vel enim finibus commodo at et nisi. Nam lacinia, quam ac bibendum molestie, tellus augue tincidunt risus, vel bibendum nisi velit euismod nunc.</p>
                                    <a href="#" class="btn btn-primary mt-3">View Project</a>
                                </div>
                            </div>
                        </div>
                        <div class="col-lg-4 col-md-6 mb-5">
                            <div class="card">
                                <img class="card-img-top" src="https://source.unsplash.com/500x300/?marketing" alt="Marketing Project">
                                <div class="card-body">
                                    <h5 class="card-title fw-bold mb-3">Marketing Project</h5>
                                    <p class="card-text">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin accumsan lacus non neque vehicula, ac blandit tortor tempor. Duis quis felis vel enim finibus commodo at et nisi. Nam lacinia, quam ac bibendum molestie, tellus augue tincidunt risus, vel bibendum nisi velit euismod nunc.</p>
                                    <a href="#" class="btn btn-primary mt-3">View Project</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            <!-- Contact Section-->
            <section class="bg-light py-5" id="contact">
                <div class="container px-5">
                    <div class="text-center">
                        <h2 class="display-5 fw-bolder"><span class="text-gradient d-inline">Contact Me</span></h2>
                    </div>
                    <div class="row gx-5 justify-content-center">
                        <div class="col-lg-6">
                            <form>
                                <div class="mb-3">
                                    <label for="name" class="form-label">Name</label>
                                    <input type="text" class="form-control" id="name" placeholder="Enter your name">
                                </div>
                                <div class="mb-3">
                                    <label for="email" class="form-label">Email address</label>
                                    <input type="email" class="form-control" id="email" placeholder="name@example.com">
                                </div>
                                <div class="mb-3">
                                    <label for="message" class="form-label">Message</label>
                                    <textarea class="form-control" id="message" rows="6" placeholder="Enter your message"></textarea>
                                </div>
                                <div class="d-grid">
                                    <button type="submit" class="btn btn-primary btn-lg fw-bold">Submit</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </section>
        </main>
        <!-- Footer-->
        <footer class="bg-white py-4 mt-auto">
            <div class="container px-5">
                <div class="row align-items-center justify-content-between flex-column flex-sm-row">
                    <div class="col-auto"><div class="small m-0">© 2021 All Rights Reserved.</div></div>
                    <div class="col-auto">
                        <a class="small" href="#">Privacy Policy</a>
                        <span class="mx-1">·</span>
                        <a class="small" href="#">Terms &amp; Conditions</a>
                        <span class="mx-1">·</span>
                        <a class="small" href="#">Contact</a>
                    </div>
                </div>
            </div>
        </footer>
    </div></body>'''},
        {'Resume Page Example 1': '''
        <body class="d-flex flex-column h-100 bg-light">
        <main class="flex-shrink-0">
            <!-- Page Content-->
            <div class="container px-5 my-5">
                <div class="text-center mb-5">
                    <h1 class="display-5 fw-bolder mb-0"><span class="text-gradient d-inline">Resume</span></h1>
                </div>
                <div class="row gx-5 justify-content-center">
                    <div class="col-lg-11 col-xl-9 col-xxl-8">
                        <!-- Experience Section-->
                        <section>
                            <div class="d-flex align-items-center justify-content-between mb-4">
                                <h2 class="text-primary fw-bolder mb-0">Experience</h2>
                                <a class="btn btn-primary px-4 py-3" href="#!">
                                    <div class="d-inline-block bi bi-download me-2"></div>
                                    Download Resume
                                </a>
                            </div>
                            <!-- Experience Card 1-->
                            <div class="card shadow border-0 rounded-4 mb-5">
                                <div class="card-body p-5">
                                    <div class="row align-items-center gx-5">
                                        <div class="col text-center text-lg-start mb-4 mb-lg-0">
                                            <div class="bg-light p-4 rounded-4">
                                                <div class="text-primary fw-bolder mb-2">2019 - Present</div>
                                                <div class="small fw-bolder">Web Developer</div>
                                                <div class="small text-muted">Stark Industries</div>
                                                <div class="small text-muted">Los Angeles, CA</div>
                                            </div>
                                        </div>
                                        <div class="col-lg-8"><div>Lorem ipsum dolor sit amet consectetur adipisicing elit. Delectus laudantium, voluptatem quis repellendus eaque sit animi illo ipsam amet officiis corporis sed aliquam non voluptate corrupti excepturi maxime porro fuga.</div></div>
                                    </div>
                                </div>
                            </div>
                        </section>
                        <!-- Education Section-->
                        <section>
                            <h2 class="text-secondary fw-bolder mb-4">Education</h2>
                            <!-- Education Card 1-->
                            <div class="card shadow border-0 rounded-4 mb-5">
                                <div class="card-body p-5">
                                    <div class="row align-items-center gx-5">
                                        <div class="col text-center text-lg-start mb-4 mb-lg-0">
                                            <div class="bg-light p-4 rounded-4">
                                                <div class="text-secondary fw-bolder mb-2">2015 - 2017</div>
                                                <div class="mb-2">
                                                    <div class="small fw-bolder">Barnett College</div>
                                                    <div class="small text-muted">Fairfield, NY</div>
                                                </div>
                                                <div class="fst-italic">
                                                    <div class="small text-muted">Master's</div>
                                                    <div class="small text-muted">Web Development</div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-lg-8"><div>Lorem ipsum dolor sit amet consectetur adipisicing elit. Delectus laudantium, voluptatem quis repellendus eaque sit animi illo ipsam amet officiis corporis sed aliquam non voluptate corrupti excepturi maxime porro fuga.</div></div>
                                    </div>
                                </div>
                            </div>
                        </section>
                        <!-- Divider-->
                        <div class="pb-5"></div>
                        <!-- Skills Section-->
                        <section>
                            <!-- Skillset Card-->
                            <div class="card shadow border-0 rounded-4 mb-5">
                                <div class="card-body p-5">
                                    <!-- Professional skills list-->
                                    <div class="mb-5">
                                        <div class="d-flex align-items-center mb-4">
                                            <div class="feature bg-primary bg-gradient-primary-to-secondary text-white rounded-3 me-3"><i class="bi bi-tools"></i></div>
                                            <h3 class="fw-bolder mb-0"><span class="text-gradient d-inline">Professional Skills</span></h3>
                                        </div>
                                        <div class="row row-cols-1 row-cols-md-3 mb-4">
                                            <div class="col mb-4 mb-md-0"><div class="d-flex align-items-center bg-light rounded-4 p-3 h-100">SEO/SEM Marketing</div></div>
                                            <div class="col mb-4 mb-md-0"><div class="d-flex align-items-center bg-light rounded-4 p-3 h-100">Statistical Analysis</div></div>
                                            <div class="col"><div class="d-flex align-items-center bg-light rounded-4 p-3 h-100">Web Development</div></div>
                                        </div>
                                        <div class="row row-cols-1 row-cols-md-3">
                                            <div class="col mb-4 mb-md-0"><div class="d-flex align-items-center bg-light rounded-4 p-3 h-100">Network Security</div></div>
                                            <div class="col mb-4 mb-md-0"><div class="d-flex align-items-center bg-light rounded-4 p-3 h-100">Adobe Software Suite</div></div>
                                            <div class="col"><div class="d-flex align-items-center bg-light rounded-4 p-3 h-100">User Interface Design</div></div>
                                        </div>
                                    </div>
                                    <!-- Languages list-->
                                    <div class="mb-0">
                                        <div class="d-flex align-items-center mb-4">
                                            <div class="feature bg-primary bg-gradient-primary-to-secondary text-white rounded-3 me-3"><i class="bi bi-code-slash"></i></div>
                                            <h3 class="fw-bolder mb-0"><span class="text-gradient d-inline">Languages</span></h3>
                                        </div>
                                        <div class="row row-cols-1 row-cols-md-3 mb-4">
                                            <div class="col mb-4 mb-md-0"><div class="d-flex align-items-center bg-light rounded-4 p-3 h-100">HTML</div></div>
                                            <div class="col mb-4 mb-md-0"><div class="d-flex align-items-center bg-light rounded-4 p-3 h-100">CSS</div></div>
                                            <div class="col"><div class="d-flex align-items-center bg-light rounded-4 p-3 h-100">JavaScript</div></div>
                                        </div>
                                        <div class="row row-cols-1 row-cols-md-3">
                                            <div class="col mb-4 mb-md-0"><div class="d-flex align-items-center bg-light rounded-4 p-3 h-100">Python</div></div>
                                            <div class="col mb-4 mb-md-0"><div class="d-flex align-items-center bg-light rounded-4 p-3 h-100">Ruby</div></div>
                                            <div class="col"><div class="d-flex align-items-center bg-light rounded-4 p-3 h-100">Node.js</div></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </section>
                    </div>
                </div>
            </div>
        </main>
    </body>'''}, 
    {'Portfolio Page Example 2': '''
    <body class="d-flex flex-column h-100">
        <main class="flex-shrink-0">
            <!-- Header-->
            <header class="py-5">
                <div class="container px-5 pb-5">
                    <div class="row gx-5 align-items-center">
                        <div class="col-xxl-5">
                            <!-- Header text content-->
                            <div class="text-center text-xxl-start">
                                <div class="badge bg-gradient-primary-to-secondary text-white mb-4"><div class="text-uppercase">Design &middot; Development &middot; Marketing</div></div>
                                <div class="fs-3 fw-light text-muted">I can help your business to</div>
                                <h1 class="display-3 fw-bolder mb-5"><span class="text-gradient d-inline">Get online and grow fast</span></h1>
                                <div class="d-grid gap-3 d-sm-flex justify-content-sm-center justify-content-xxl-start mb-3">
                                    <a class="btn btn-primary btn-lg px-5 py-3 me-sm-3 fs-6 fw-bolder" href="resume.html">Resume</a>
                                    <a class="btn btn-outline-dark btn-lg px-5 py-3 fs-6 fw-bolder" href="projects.html">Projects</a>
                                </div>
                            </div>
                        </div>
                        <div class="col-xxl-7">
                            <!-- Header profile picture-->
                            <div class="d-flex justify-content-center mt-5 mt-xxl-0">
                                <div class="profile bg-gradient-primary-to-secondary">
                                    <!-- TIP: For best results, use a photo with a transparent background like the demo example below-->
                                    <!-- Watch a tutorial on how to do this on YouTube (link)-->
                                    <img class="profile-img" src="assets/profile.png" alt="..." />
                                    <div class="dots-1">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </header>
            <!-- About Section-->
            <section class="bg-light py-5">
                <div class="container px-5">
                    <div class="row gx-5 justify-content-center">
                        <div class="col-xxl-8">
                            <div class="text-center my-5">
                                <h2 class="display-5 fw-bolder"><span class="text-gradient d-inline">About Me</span></h2>
                                <p class="lead fw-light mb-4">My name is Start Bootstrap and I help brands grow.</p>
                                <p class="text-muted">Lorem ipsum dolor sit amet, consectetur adipisicing elit. Fugit dolorum itaque qui unde quisquam consequatur autem. Eveniet quasi nobis aliquid cumque officiis sed rem iure ipsa! Praesentium ratione atque dolorem?</p>
                                <div class="d-flex justify-content-center fs-2 gap-4">
                                    <a class="text-gradient" href="#!"><i class="bi bi-twitter"></i></a>
                                    <a class="text-gradient" href="#!"><i class="bi bi-linkedin"></i></a>
                                    <a class="text-gradient" href="#!"><i class="bi bi-github"></i></a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </main>
        <!-- Footer-->
        <footer class="bg-white py-4 mt-auto">
            <div class="container px-5">
                <div class="row align-items-center justify-content-between flex-column flex-sm-row">
                    <div class="col-auto"><div class="small m-0">Copyright &copy; Your Website 2023</div></div>
                    <div class="col-auto">
                        <a class="small" href="#!">Privacy</a>
                        <span class="mx-1">&middot;</span>
                        <a class="small" href="#!">Terms</a>
                        <span class="mx-1">&middot;</span>
                        <a class="small" href="#!">Contact</a>
                    </div>
                </div>
            </div>
        </footer>
    </body>
'''}, 
    {'Login Page Example 1': '''
    <section class="h-100 gradient-form" style="background-color: #eee;">
    <div class="container py-5 h-100">
        <div class="row d-flex justify-content-center align-items-center h-100">
        <div class="col-xl-10">
            <div class="card rounded-3 text-black">
            <div class="row g-0">
                <div class="col-lg-6">
                <div class="card-body p-md-5 mx-md-4">

                    <div class="text-center">
                    <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-login-form/lotus.webp"
                        style="width: 185px;" alt="logo">
                    <h4 class="mt-1 mb-5 pb-1">We are The Lotus Team</h4>
                    </div>

                    <form>
                    <p>Please login to your account</p>

                    <div class="form-outline mb-4">
                        <input type="email" id="form2Example11" class="form-control"
                        placeholder="Phone number or email address" />
                        <label class="form-label" for="form2Example11">Username</label>
                    </div>

                    <div class="form-outline mb-4">
                        <input type="password" id="form2Example22" class="form-control" />
                        <label class="form-label" for="form2Example22">Password</label>
                    </div>

                    <div class="text-center pt-1 mb-5 pb-1">
                        <button class="btn btn-primary btn-block fa-lg gradient-custom-2 mb-3" type="button">Log
                        in</button>
                        <a class="text-muted" href="#!">Forgot password?</a>
                    </div>

                    <div class="d-flex align-items-center justify-content-center pb-4">
                        <p class="mb-0 me-2">Don't have an account?</p>
                        <button type="button" class="btn btn-outline-danger">Create new</button>
                    </div>

                    </form>

                </div>
                </div>
                <div class="col-lg-6 d-flex align-items-center gradient-custom-2">
                <div class="text-white px-3 py-4 p-md-5 mx-md-4">
                    <h4 class="mb-4">We are more than just a company</h4>
                    <p class="small mb-0">Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
                    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud
                    exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
                </div>
                </div>
            </div>
            </div>
        </div>
        </div>
    </div>
    </section>
        '''},
    {'Portfolio Page Example 1': '''
    <body id="page-top">
                <!-- Header Section -->
                <header class="bg-dark text-white py-5">
                    <div class="container">
                    <div class="row">
                        <div class="col-lg-6">
                        <h1 class="display-4 fw-bold">Your Name Here</h1>
                        <p class="lead mb-0">Web Developer | Designer | Photographer</p>
                        </div>
                    </div>
                    </div>
                </header>

                <!-- About Section -->
                <section class="bg-secondary py-5">
                    <div class="container">
                    <div class="row">
                        <div class="col-lg-6">
                        <h2 class="fw-bold mb-4">About Me</h2>
                        <p class="lead mb-4">I am a multi-disciplinary creative with a passion for web development, design, and photography. I have experience working with clients from various industries and creating unique solutions for their needs.</p>
                        <a href="#" class="btn btn-dark rounded-pill px-4">Learn More</a>
                        </div>
                        <div class="col-lg-6">
                        <img src="https://source.unsplash.com/900x600/?portrait" class="img-fluid rounded" alt="Portrait">
                        </div>
                    </div>
                    </div>
                </section>

                <!-- Portfolio Section -->
                <section class="py-5">
                    <div class="container">
                    <h2 class="fw-bold mb-4">Portfolio</h2>
                    <div class="row gx-5">
                        <div class="col-lg-4 mb-5">
                        <div class="card h-100 border-0 shadow">
                            <img src="https://source.unsplash.com/400x300/?webdesign" class="card-img-top" alt="Web Design">
                            <div class="card-body">
                            <h5 class="card-title fw-bold mb-3">Web Design</h5>
                            <p class="card-text">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed blandit, nisl ac hendrerit mattis, nulla mauris bibendum nisl, vel luctus dolor libero vel velit.</p>
                            <a href="#" class="btn btn-dark rounded-pill px-4">View Project</a>
                            </div>
                        </div>
                        </div>
                        <div class="col-lg-4 mb-5">
                        <div class="card h-100 border-0 shadow">
                            <img src="https://source.unsplash.com/400x300/?photography" class="card-img-top" alt="Photography">
                            <div class="card-body">
                            <h5 class="card-title fw-bold mb-3">Photography</h5>
                            <p class="card-text">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed blandit, nisl ac hendrerit mattis, nulla mauris bibendum nisl, vel luctus dolor libero vel velit.</p>
                            <a href="#" class="btn btn-dark rounded-pill px-4">View Project</a>
                            </div>
                        </div>
                        </div>
                        <div class="col-lg-4 mb-5">
                        <div class="card h-100 border-0 shadow">
                            <img src="https://source.unsplash.com/400x300/?development" class="card-img-top" alt="Development">
                            <div class="card-body">
                            <h5 class="card-title fw-bold mb-3">Development</h5>
                            <p class="card-text">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed blandit, nisl ac hendrerit mattis, nulla mauris bibendum nisl, vel luctus dolor libero vel velit.</p>
                            <a href="#" class="btn btn-dark rounded-pill px-4">View Project</a>
                            </div>
                        </div>
                        </div>
                    </div>
                    </div>
                </section>

                <!-- Achievements Section -->
                <section class="bg-dark text-white py-5">
                    <div class="container">
                    <h2 class="fw-bold mb-4">Achievements</h2>
                    <div class="row gx-5">
                        <div class="col-lg-3 col-md-6 mb-4 mb-lg-0">
                        <div class="card h-100 border-0 shadow">
                            <div class="card-body">
                            <h5 class="card-title fw-bold mb-3">Clients</h5>
                            <p class="card-text display-6">25+</p>
                            </div>
                        </div>
                        </div>
                        <div class="col-lg-3 col-md-6 mb-4 mb-lg-0">
                        <div class="card h-100 border-0 shadow">
                            <div class="card-body">
                            <h5 class="card-title fw-bold mb-3">Projects</h5>
                            <p class="card-text display-6">50+</p>
                            </div>
                        </div>
                        </div>
                        <div class="col-lg-3 col-md-6 mb-4 mb-md-0">
                        <div class="card h-100 border-0 shadow">
                            <div class="card-body">
                            <h5 class="card-title fw-bold mb-3">Awards</h5>
                            <p class="card-text display-6">5</p>
                            </div>
                        </div>
                        </div>
                        <div class="col-lg-3 col-md-6">
                        <div class="card h-100 border-0 shadow">
                            <div class="card-body">
                            <h5 class="card-title fw-bold mb-3">Years of Experience</h5>
                            <p class="card-text display-6">10+</p>
                            </div>
                        </div>
                        </div>
                    </div>
                    </div>
                </section>

                <!-- Contact Section -->
                <section class="py-5">
                    <div class="container">
                    <h2 class="fw-bold mb-4">Contact Me</h2>
                    <div class="row gx-5">
                        <div class="col-lg-6">
                        <form>
                            <div class="mb-3">
                            <label for="name" class="form-label fw-bold">Name</label>
                            <input type="text" class="form-control" id="name" placeholder="Enter your name">
                            </div>
                            <div class="mb-3">
                            <label for="email" class="form-label fw-bold">Email address</label>
                            <input type="email" class="form-control" id="email" placeholder="Enter your email">
                            </div>
                            <div class="mb-3">
                            <label for="message" class="form-label fw-bold">Message</label>
                            <textarea class="form-control" id="message" rows="5" placeholder="Enter your message"></textarea>
                            </div>
                            <button type="submit" class="btn btn-dark rounded-pill px-4">Submit</button>
                        </form>
                        </div>
                        <div class="col-lg-6">
                        <div class="card h-100 border-0 shadow">
                            <div class="card-body">
                            <h5 class="card-title fw-bold mb-3">Contact Information</h5>
                            <p class="card-text">123 Main St<br>Anytown, USA 12345<br><br>Email: info@shaunoffenbacher.com<br>Phone: (123) 456-7890</p>
                            </div>
                        </div>
                        </div>
                    </div>
                    </div>
                </section>

                <!-- Footer Section -->
                <footer class="bg-dark text-white py-5">
                    <div class="container">
                    <div class="row">
                        <div class="col-lg-6">
                        <p class="lead mb-0">© Shaun Offenbacher 2021</p>
                        </div>
                        <div class="col-lg-6">
                        <p class="lead mb-0 text-end">Designed with <i class="bi bi-heart-fill text-danger"></i> by Shaun Offenbacher</p>
                        </div>
                    </div>
                    </div>
                </footer>
        </body>

        '''},
    {'Login Page Example 2': '''
            <section class="vh-100">
  <div class="container py-5 h-100">
    <div class="row d-flex align-items-center justify-content-center h-100">
      <div class="col-md-8 col-lg-7 col-xl-6">
        <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-login-form/draw2.svg"
          class="img-fluid" alt="Phone image">
      </div>
      <div class="col-md-7 col-lg-5 col-xl-5 offset-xl-1">
        <form>
          <!-- Email input -->
          <div class="form-outline mb-4">
            <input type="email" id="form1Example13" class="form-control form-control-lg" />
            <label class="form-label" for="form1Example13">Email address</label>
          </div>

          <!-- Password input -->
          <div class="form-outline mb-4">
            <input type="password" id="form1Example23" class="form-control form-control-lg" />
            <label class="form-label" for="form1Example23">Password</label>
          </div>

          <div class="d-flex justify-content-around align-items-center mb-4">
            <!-- Checkbox -->
            <div class="form-check">
              <input class="form-check-input" type="checkbox" value="" id="form1Example3" checked />
              <label class="form-check-label" for="form1Example3"> Remember me </label>
            </div>
            <a href="#!">Forgot password?</a>
          </div>

          <!-- Submit button -->
          <button type="submit" class="btn btn-primary btn-lg btn-block">Sign in</button>

          <div class="divider d-flex align-items-center my-4">
            <p class="text-center fw-bold mx-3 mb-0 text-muted">OR</p>
          </div>

          <a class="btn btn-primary btn-lg btn-block" style="background-color: #3b5998" href="#!"
            role="button">
            <i class="fab fa-facebook-f me-2"></i>Continue with Facebook
          </a>
          <a class="btn btn-primary btn-lg btn-block" style="background-color: #55acee" href="#!"
            role="button">
            <i class="fab fa-twitter me-2"></i>Continue with Twitter</a>
        </form>
      </div>
    </div>
  </div>
</section>

        '''}
]
}
def main():
    for example in examples['body']:
        pprint.pprint(list(example.keys())[0])

if __name__ == '__main__':
    main()