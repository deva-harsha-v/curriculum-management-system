"""
Management command to seed a comprehensive, realistic academic dataset
for Sri Vasavi Engineering College (Department of Computer Science & Engineering, R23).
Fully idempotent: running multiple times updates or preserves records without duplicating.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import Department, Profile
from curriculum.models import (
    CurriculumVersion, GraduateAttribute, PEO, MissionPEOMapping,
    PEOGAMapping, ProgramOutcome, POPEOMapping, CourseCategory,
    Semester, Course, CourseOutcome, COPOMapping, ReferenceBook,
    ChangeRequest, AuditLog
)


class Command(BaseCommand):
    help = "Seed comprehensive, realistic demo academic data for CSE R23 curriculum and workflows."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=" * 70))
        self.stdout.write(self.style.NOTICE("STARTING DEMO ACADEMIC DATA SEEDING"))
        self.stdout.write(self.style.NOTICE("=" * 70))

        # Ensure demo users exist first
        try:
            call_command("seed_demo_users")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"seed_demo_users notice: {e}"))

        stats = {
            "departments": {"created": 0, "existing": 0},
            "curriculum_versions": {"created": 0, "existing": 0},
            "course_categories": {"created": 0, "existing": 0},
            "graduate_attributes": {"created": 0, "existing": 0},
            "peos": {"created": 0, "existing": 0},
            "mission_peo_mappings": {"created": 0, "existing": 0},
            "peo_ga_mappings": {"created": 0, "existing": 0},
            "program_outcomes": {"created": 0, "existing": 0},
            "po_peo_mappings": {"created": 0, "existing": 0},
            "semesters": {"created": 0, "existing": 0},
            "courses": {"created": 0, "existing": 0},
            "course_outcomes": {"created": 0, "existing": 0},
            "copo_mappings": {"created": 0, "existing": 0},
            "reference_books": {"created": 0, "existing": 0},
            "change_requests": {"created": 0, "existing": 0},
            "audit_logs": {"created": 0, "existing": 0},
        }

        # ── 1. Department ────────────────────────────────────────────────────────
        dept, created = Department.objects.get_or_create(
            code="CSE",
            defaults={
                "name": "Computer Science and Engineering",
                "degree": "B.Tech",
            }
        )
        if created:
            stats["departments"]["created"] += 1
            self.stdout.write(self.style.SUCCESS(f"Created Department: {dept}"))
        else:
            stats["departments"]["existing"] += 1
            dept.name = "Computer Science and Engineering"
            dept.degree = "B.Tech"
            dept.save()

        # Users
        admin_user = User.objects.filter(username="admin").first()
        hod_user = User.objects.filter(username="hod_cse").first()
        faculty_user = User.objects.filter(username="faculty_cse").first()

        # ── 2. Institute & Department Vision / Mission ───────────────────────────
        inst_name = "Sri Vasavi Engineering College"
        inst_vision = (
            "To be a center of excellence in engineering education, research, innovation, "
            "and entrepreneurship, nurturing competent professionals with ethical values "
            "and a commitment to societal development."
        )
        inst_mission = [
            "To provide quality technical education through innovative teaching and learning practices.",
            "To promote research, innovation, entrepreneurship, and industry collaboration.",
            "To develop professionally competent graduates with ethical values and social responsibility.",
            "To foster an inclusive learning environment that encourages lifelong learning and holistic development.",
            "To contribute to the technological and socio-economic development of society through engineering knowledge and innovation.",
        ]

        dept_vision = (
            "To emerge as a center of excellence in Computer Science and Engineering by providing "
            "quality education, fostering innovation and research, and developing industry-ready "
            "professionals with ethical and social responsibility."
        )
        dept_mission = [
            "To provide quality education in Computer Science and Engineering through effective teaching-learning practices and modern technologies.",
            "To develop strong technical, analytical, problem-solving, and programming skills among students.",
            "To promote research, innovation, entrepreneurship, and industry-oriented projects in emerging areas of computing.",
            "To inculcate professional ethics, teamwork, leadership, and social responsibility among students.",
            "To prepare graduates for successful careers, higher education, and lifelong learning in the field of Computer Science and Engineering.",
        ]

        ga_intro = (
            "The Graduate Attributes are the knowledge, skills, and attitudes that students are "
            "expected to possess at the time of graduation. These attributes are generic in nature "
            "and are common to engineering programs. They represent the qualities required for graduates "
            "to contribute effectively to professional practice, innovation, and society."
        )

        # ── 3. Curriculum Version (R23 - Draft) ───────────────────────────────────
        version, created = CurriculumVersion.objects.get_or_create(
            department=dept,
            regulation="R23",
            defaults={
                "academic_year": "2023-24",
                "status": CurriculumVersion.STATUS_DRAFT,
                "institute_name": inst_name,
                "institute_vision": inst_vision,
                "institute_mission": inst_mission,
                "dept_vision": dept_vision,
                "dept_mission": dept_mission,
                "ga_intro": ga_intro,
                "created_by": admin_user,
            }
        )
        if created:
            stats["curriculum_versions"]["created"] += 1
            self.stdout.write(self.style.SUCCESS(f"Created CurriculumVersion: {version}"))
        else:
            stats["curriculum_versions"]["existing"] += 1
            version.academic_year = "2023-24"
            version.institute_name = inst_name
            version.institute_vision = inst_vision
            version.institute_mission = inst_mission
            version.dept_vision = dept_vision
            version.dept_mission = dept_mission
            version.ga_intro = ga_intro
            version.save()

        # Also ensure a Published historical version exists (R20) for demonstration of immutable published records
        pub_version, p_created = CurriculumVersion.objects.get_or_create(
            department=dept,
            regulation="R20",
            defaults={
                "academic_year": "2020-21",
                "status": CurriculumVersion.STATUS_PUBLISHED,
                "institute_name": inst_name,
                "institute_vision": inst_vision,
                "institute_mission": inst_mission,
                "dept_vision": dept_vision,
                "dept_mission": dept_mission,
                "ga_intro": ga_intro,
                "created_by": admin_user,
            }
        )
        if p_created:
            stats["curriculum_versions"]["created"] += 1
        else:
            stats["curriculum_versions"]["existing"] += 1

        # ── 4. Graduate Attributes (GA1 .. GA12) ──────────────────────────────────
        ga_data = [
            (1, "Engineering Knowledge", "Apply the knowledge of mathematics, science, engineering fundamentals, and computer science specialization to the solution of complex engineering problems."),
            (2, "Problem Analysis", "Identify, formulate, review research literature, and analyze complex engineering problems reaching substantiated conclusions using first principles of mathematics, natural sciences, and engineering sciences."),
            (3, "Design/Development of Solutions", "Design solutions for complex engineering problems and design system components or processes that meet the specified needs with appropriate consideration for public health and safety, cultural, societal, and environmental factors."),
            (4, "Conduct Investigations of Complex Problems", "Use research-based knowledge and research methods including design of experiments, analysis and interpretation of data, and synthesis of information to provide valid conclusions."),
            (5, "Modern Tool Usage", "Create, select, and apply appropriate techniques, resources, and modern engineering and IT tools including prediction and modeling to complex engineering activities with an understanding of limitations."),
            (6, "The Engineer and Society", "Apply reasoning informed by contextual knowledge to assess societal, health, safety, legal and cultural issues and the consequent responsibilities relevant to professional engineering practice."),
            (7, "Environment and Sustainability", "Understand the impact of professional engineering solutions in societal and environmental contexts, and demonstrate knowledge of, and need for sustainable development."),
            (8, "Ethics", "Apply ethical principles and commit to professional ethics and responsibilities and norms of the engineering practice."),
            (9, "Individual and Team Work", "Function effectively as an individual, and as a member or leader in diverse teams, and in multidisciplinary settings."),
            (10, "Communication", "Communicate effectively on complex engineering activities with the engineering community and society at large through reports, presentations, and clear instructions."),
            (11, "Project Management and Finance", "Demonstrate knowledge and understanding of engineering and management principles and apply these to manage projects in multidisciplinary environments."),
            (12, "Life-long Learning", "Recognize the need for, and have the preparation and ability to engage in independent and lifelong learning in the broadest context of technological change."),
        ]
        for num, title, desc in ga_data:
            ga, c = GraduateAttribute.objects.get_or_create(
                curriculum_version=version,
                number=num,
                defaults={"title": title, "description": desc}
            )
            if c:
                stats["graduate_attributes"]["created"] += 1
            else:
                stats["graduate_attributes"]["existing"] += 1
                ga.title = title
                ga.description = desc
                ga.save()

        # ── 5. Program Educational Objectives (PEO1 .. PEO3) ─────────────────────
        peo_data = [
            (1, "Graduates will establish successful careers in software development, computing, information technology, and related professional fields."),
            (2, "Graduates will pursue innovation, higher education, research, and entrepreneurship to address evolving technological challenges."),
            (3, "Graduates will demonstrate professional ethics, effective communication, teamwork, leadership, and social responsibility."),
        ]
        peo_objs = {}
        for num, desc in peo_data:
            peo, c = PEO.objects.get_or_create(
                curriculum_version=version,
                number=num,
                defaults={"description": desc}
            )
            peo_objs[num] = peo
            if c:
                stats["peos"]["created"] += 1
            else:
                stats["peos"]["existing"] += 1
                peo.description = desc
                peo.save()

        # ── 6. Mission to PEO Mappings ───────────────────────────────────────────
        mission_peo_ratings = [
            (1, dept_mission[0], {"1": 3, "2": 2, "3": 1}),
            (2, dept_mission[1], {"1": 3, "2": 3, "3": 1}),
            (3, dept_mission[2], {"1": 2, "2": 3, "3": 2}),
            (4, dept_mission[3], {"1": 1, "2": 1, "3": 3}),
            (5, dept_mission[4], {"1": 3, "2": 3, "3": 2}),
        ]
        for order, stmt, mapping_dict in mission_peo_ratings:
            m_peo, c = MissionPEOMapping.objects.get_or_create(
                curriculum_version=version,
                mission_order=order,
                defaults={"mission_statement": stmt, "mappings": mapping_dict}
            )
            if c:
                stats["mission_peo_mappings"]["created"] += 1
            else:
                stats["mission_peo_mappings"]["existing"] += 1
                m_peo.mission_statement = stmt
                m_peo.mappings = mapping_dict
                m_peo.save()

        # ── 7. PEO to GA Mappings ────────────────────────────────────────────────
        peo_ga_ratings = [
            (1, {"1": 3, "2": 3, "3": 3, "4": 2, "5": 3, "8": 2, "9": 2, "10": 2, "11": 2, "12": 3}),
            (2, {"1": 3, "2": 3, "3": 3, "4": 3, "5": 3, "6": 2, "7": 2, "11": 2, "12": 3}),
            (3, {"6": 3, "7": 2, "8": 3, "9": 3, "10": 3, "11": 2, "12": 3}),
        ]
        for peo_num, ga_map in peo_ga_ratings:
            peo = peo_objs.get(peo_num)
            if peo:
                p_ga, c = PEOGAMapping.objects.get_or_create(
                    curriculum_version=version,
                    peo=peo,
                    defaults={"mappings": ga_map}
                )
                if c:
                    stats["peo_ga_mappings"]["created"] += 1
                else:
                    stats["peo_ga_mappings"]["existing"] += 1
                    p_ga.mappings = ga_map
                    p_ga.save()

        # ── 8. Program Outcomes (PO1 .. PO12 + PSO1 .. PSO3) ─────────────────────
        po_data = [
            (1, "Engineering Knowledge: Apply mathematics, science, and computing fundamentals to solve complex engineering problems."),
            (2, "Problem Analysis: Identify, formulate, and analyze complex engineering and computing problems reaching substantiated conclusions."),
            (3, "Design/Development of Solutions: Design solutions for complex computer science problems and system architectures that meet specified needs."),
            (4, "Conduct Investigations: Conduct investigations of complex problems using research-based knowledge and computing research methods."),
            (5, "Modern Tool Usage: Select and apply modern engineering and IT software tools, libraries, and frameworks to complex computing activities."),
            (6, "The Engineer and Society: Assess societal, health, safety, and legal issues relevant to professional computer science engineering practice."),
            (7, "Environment and Sustainability: Understand the impact of software and computing systems in societal and environmental contexts for sustainable development."),
            (8, "Ethics: Apply ethical principles and commit to professional ethics, responsibilities, and cyber standards."),
            (9, "Individual and Team Work: Function effectively as an individual, and as a member or leader in diverse and multidisciplinary teams."),
            (10, "Communication: Communicate effectively on technical computing activities with engineering peers and society through documentation and presentations."),
            (11, "Project Management and Finance: Apply software engineering and project management principles to manage software projects effectively."),
            (12, "Life-long Learning: Recognize the need for and have the ability to engage in independent and lifelong learning in computing."),
            (13, "PSO1: Apply programming, data structures, algorithms, databases, and software engineering principles to develop computing solutions."),
            (14, "PSO2: Apply modern computing tools and technologies to analyze and solve real-world problems in emerging areas of computing."),
            (15, "PSO3: Design and implement secure, scalable, and socially responsible software systems adhering to professional engineering standards."),
        ]
        po_objs = {}
        for num, desc in po_data:
            po, c = ProgramOutcome.objects.get_or_create(
                curriculum_version=version,
                number=num,
                defaults={"description": desc}
            )
            po_objs[num] = po
            if c:
                stats["program_outcomes"]["created"] += 1
            else:
                stats["program_outcomes"]["existing"] += 1
                po.description = desc
                po.save()

        # ── 9. PO to PEO Mappings ────────────────────────────────────────────────
        po_peo_ratings = {
            1: {"1": 3, "2": 2},
            2: {"1": 3, "2": 3},
            3: {"1": 3, "2": 3, "3": 1},
            4: {"1": 2, "2": 3},
            5: {"1": 3, "2": 2},
            6: {"3": 3},
            7: {"2": 1, "3": 2},
            8: {"3": 3},
            9: {"1": 2, "3": 3},
            10: {"3": 3},
            11: {"1": 2, "3": 2},
            12: {"1": 2, "2": 3, "3": 2},
            13: {"1": 3, "2": 2},
            14: {"1": 2, "2": 3},
            15: {"1": 3, "2": 2, "3": 3},
        }
        for po_num, peo_map in po_peo_ratings.items():
            po = po_objs.get(po_num)
            if po:
                po_peo, c = POPEOMapping.objects.get_or_create(
                    curriculum_version=version,
                    program_outcome=po,
                    defaults={"mappings": peo_map}
                )
                if c:
                    stats["po_peo_mappings"]["created"] += 1
                else:
                    stats["po_peo_mappings"]["existing"] += 1
                    po_peo.mappings = peo_map
                    po_peo.save()

        # ── 10. Course Categories ────────────────────────────────────────────────
        cat_data = [
            ("BSC", "Basic Science Courses", 21, 19, 1),
            ("ESC", "Engineering Science Courses", 24, 22, 2),
            ("PCC", "Professional Core Courses", 58, 54, 3),
            ("DEC", "Professional Elective Courses", 15, 15, 4),
            ("OPC", "Open Elective Courses", 12, 12, 5),
            ("HSC", "Humanities and Social Sciences", 12, 10, 6),
            ("PRC", "Project Work & Internship", 16, 16, 7),
            ("MDC", "Mandatory Audit Courses", 0, 0, 8),
        ]
        cat_objs = {}
        for code, name, offered, min_c, disp in cat_data:
            cat, c = CourseCategory.objects.get_or_create(
                curriculum_version=version,
                code=code,
                defaults={
                    "name": name,
                    "credits_offered": offered,
                    "min_credits": min_c,
                    "display_order": disp,
                }
            )
            cat_objs[code] = cat
            if c:
                stats["course_categories"]["created"] += 1
            else:
                stats["course_categories"]["existing"] += 1
                cat.name = name
                cat.credits_offered = offered
                cat.min_credits = min_c
                cat.display_order = disp
                cat.save()

        # ── 11. Semesters (II-I and II-II) ───────────────────────────────────────
        sem_2_1, c21 = Semester.objects.get_or_create(
            curriculum_version=version,
            year=2,
            semester=1
        )
        if c21:
            stats["semesters"]["created"] += 1
        else:
            stats["semesters"]["existing"] += 1

        sem_2_2, c22 = Semester.objects.get_or_create(
            curriculum_version=version,
            year=2,
            semester=2
        )
        if c22:
            stats["semesters"]["created"] += 1
        else:
            stats["semesters"]["existing"] += 1

        # ── 12. Prerequisite Courses in II-I (Year 2, Sem 1) ────────────────────
        ii_1_courses = [
            {
                "code": "CS2101",
                "title": "Data Structures",
                "category": cat_objs.get("PCC"),
                "lectures": 3, "tutorials": 0, "practicals": 0, "credits": 3,
                "display_order": 1,
                "syllabus": (
                    "UNIT I: Introduction to Data Structures, Abstract Data Types (ADTs), Linear vs Non-Linear. "
                    "Arrays, Dynamic Memory Allocation, Stacks: Implementation using Arrays & Linked Lists, Applications: "
                    "Infix to Postfix conversion, Postfix evaluation.\n\n"
                    "UNIT II: Queues: Circular Queues, Deques, Priority Queues. Linked Lists: Singly Linked Lists, "
                    "Doubly Linked Lists, Circular Linked Lists, Polynomial representation and addition using lists.\n\n"
                    "UNIT III: Trees: Binary Trees, Binary Tree Representations and Traversals (Inorder, Preorder, Postorder). "
                    "Binary Search Trees (BST): Insertion, Deletion, Search. AVL Trees: Rotations and Balance Factor, B-Trees overview.\n\n"
                    "UNIT IV: Graphs: Terminology, Representations (Adjacency Matrix & Adjacency List), Graph Traversals: "
                    "Breadth First Search (BFS), Depth First Search (DFS), Topological Sorting, Spanning Trees.\n\n"
                    "UNIT V: Sorting: Merge Sort, Quick Sort, Heap Sort. Hashing: Hash Functions, Collision Resolution: "
                    "Separate Chaining, Open Addressing (Linear Probing, Quadratic Probing, Double Hashing)."
                ),
                "cos": [
                    (1, "Understand fundamental data structures and analyze abstract data type specifications."),
                    (2, "Implement linear data structures including stacks, queues, and linked lists for computational problems."),
                    (3, "Apply tree data structures and balanced binary search trees for efficient search and retrieval."),
                    (4, "Analyze graph traversal algorithms and shortest path computation techniques."),
                    (5, "Evaluate sorting algorithms and collision-resolution hashing mechanisms."),
                ],
                "refs": [
                    (1, "Mark Allen Weiss, 'Data Structures and Algorithm Analysis in C++', 4th Edition, Pearson."),
                    (2, "Ellis Horowitz, Sartaj Sahni, Dinesh Mehta, 'Fundamentals of Data Structures in C++', Silicon Press."),
                ]
            },
            {
                "code": "CS2102",
                "title": "Computer Organization and Architecture",
                "category": cat_objs.get("PCC"),
                "lectures": 3, "tutorials": 0, "practicals": 0, "credits": 3,
                "display_order": 2,
                "syllabus": (
                    "UNIT I: Basic Computer Organization and Design: Instruction codes, Computer registers, Computer instructions, "
                    "Timing and control, Instruction cycle, Memory-reference instructions, Input-Output and interrupt.\n\n"
                    "UNIT II: Central Processing Unit: General register organization, Stack organization, Instruction formats, "
                    "Addressing modes, Data transfer and manipulation, Program control, Reduced Instruction Set Computer (RISC).\n\n"
                    "UNIT III: Computer Arithmetic: Addition and subtraction with signed-magnitude, Multiplication algorithms "
                    "(Booth multiplication algorithm), Division algorithms, Floating-point arithmetic operations.\n\n"
                    "UNIT IV: Memory Organization: Memory hierarchy, Main memory, Auxiliary memory, Associative memory, "
                    "Cache memory (Mapping functions, Replacement policies, Write policies), Virtual memory.\n\n"
                    "UNIT V: Input-Output Organization & Pipelining: Peripheral devices, Input-Output Interface, Asynchronous "
                    "data transfer, Modes of transfer, Priority Interrupt, Direct Memory Access (DMA), Pipelining and superscalar processors."
                ),
                "cos": [
                    (1, "Explain fundamental computer organization principles, registers, and instruction cycles."),
                    (2, "Analyze CPU micro-architecture, addressing modes, and RISC/CISC paradigms."),
                    (3, "Implement fixed-point and floating-point computer arithmetic algorithms."),
                    (4, "Evaluate memory hierarchy design, cache mapping techniques, and virtual memory systems."),
                    (5, "Assess I/O communication interfaces, DMA transfers, and pipelined execution."),
                ],
                "refs": [
                    (1, "M. Morris Mano, 'Computer System Architecture', 3rd Edition, Pearson Education."),
                    (2, "William Stallings, 'Computer Organization and Architecture: Designing for Performance', 10th Edition, Pearson."),
                ]
            },
            {
                "code": "CS2103",
                "title": "Object Oriented Programming through Java",
                "category": cat_objs.get("PCC"),
                "lectures": 3, "tutorials": 0, "practicals": 0, "credits": 3,
                "display_order": 3,
                "syllabus": (
                    "UNIT I: Introduction to OOP principles: Abstraction, Encapsulation, Inheritance, Polymorphism. "
                    "Java Virtual Machine (JVM), Bytecode, Data types, Variables, Operators, Control structures, Classes and Objects.\n\n"
                    "UNIT II: Inheritance: Method Overriding, super keyword, final keyword, Abstract classes, Interfaces: "
                    "Multiple inheritance through interfaces, Nested interfaces, Packages: Creating and accessing packages.\n\n"
                    "UNIT III: Exception Handling: try-catch-finally, throw, throws, Built-in and Custom exceptions. "
                    "Multithreaded Programming: Creating threads, Thread life cycle, Thread synchronization, Inter-thread communication.\n\n"
                    "UNIT IV: Java I/O and Collections: Byte and Character streams, File handling, Java Collections Framework: "
                    "List, Set, Map, ArrayList, LinkedList, HashMap, Iterators, Generics.\n\n"
                    "UNIT V: GUI Programming & Event Handling: Introduction to JavaFX/Swing components, Event Delegation Model, "
                    "Event listeners, JDBC: Architecture, Driver types, Database connectivity and executing queries."
                ),
                "cos": [
                    (1, "Apply object-oriented programming fundamentals and core Java language constructs."),
                    (2, "Design modular applications utilizing inheritance, abstract classes, interfaces, and packages."),
                    (3, "Implement robust multithreaded systems with structured exception handling."),
                    (4, "Utilize Java Collections framework and stream-based I/O for data processing."),
                    (5, "Develop GUI and database-driven desktop applications using JDBC."),
                ],
                "refs": [
                    (1, "Herbert Schildt, 'Java: The Complete Reference', 11th Edition, McGraw-Hill."),
                    (2, "Paul Deitel, Harvey Deitel, 'Java How to Program', 11th Edition, Pearson."),
                ]
            },
            {
                "code": "CS2104",
                "title": "Discrete Mathematical Structures",
                "category": cat_objs.get("BSC"),
                "lectures": 3, "tutorials": 0, "practicals": 0, "credits": 3,
                "display_order": 4,
                "syllabus": (
                    "UNIT I: Mathematical Logic: Propositional logic, Truth tables, Tautologies, Logical equivalence, "
                    "Predicates and Quantifiers, Rules of inference, Methods of proof (Direct, Contradiction, Induction).\n\n"
                    "UNIT II: Sets, Relations and Functions: Set operations, Venn diagrams, Binary relations, Equivalence relations, "
                    "Partial orderings, Hasse diagrams, Functions: Injective, Surjective, Bijective, Composition of functions.\n\n"
                    "UNIT III: Algebraic Structures & Combinatorics: Semigroups, Monoids, Groups, Subgroups, Homomorphism, "
                    "Permutations and Combinations, Pigeonhole principle, Inclusion-Exclusion principle.\n\n"
                    "UNIT IV: Recurrence Relations: Formulating recurrence relations, Solving linear recurrence relations with constant "
                    "coefficients (Homogeneous and Particular solutions), Generating functions.\n\n"
                    "UNIT V: Graph Theory: Basic graph terminology, Representation of graphs, Isomorphism, Euler and Hamiltonian paths, "
                    "Planar graphs, Graph coloring, Trees, Minimum Spanning Trees."
                ),
                "cos": [
                    (1, "Formulate mathematical arguments using propositional and predicate logic."),
                    (2, "Analyze relations, equivalence classes, and partial order sets."),
                    (3, "Apply algebraic structures and combinatorial counting principles."),
                    (4, "Solve discrete recurrence relations using generating functions."),
                    (5, "Model computational networks and structures using graph theory."),
                ],
                "refs": [
                    (1, "Kenneth H. Rosen, 'Discrete Mathematics and Its Applications', 8th Edition, McGraw-Hill."),
                    (2, "Tremblay J.P. and Manohar R, 'Discrete Mathematical Structures with Applications to Computer Science', McGraw-Hill."),
                ]
            },
        ]

        course_lookup = {}

        for cdata in ii_1_courses:
            crs, c = Course.objects.get_or_create(
                semester=sem_2_1,
                code=cdata["code"],
                defaults={
                    "title": cdata["title"],
                    "category": cdata["category"],
                    "lectures": cdata["lectures"],
                    "tutorials": cdata["tutorials"],
                    "practicals": cdata["practicals"],
                    "credits": cdata["credits"],
                    "syllabus_text": cdata["syllabus"],
                    "display_order": cdata["display_order"],
                }
            )
            course_lookup[cdata["code"]] = crs
            if c:
                stats["courses"]["created"] += 1
            else:
                stats["courses"]["existing"] += 1
                crs.title = cdata["title"]
                crs.category = cdata["category"]
                crs.syllabus_text = cdata["syllabus"]
                crs.save()

            # Course Outcomes & References
            for conum, codesc in cdata["cos"]:
                co, coc = CourseOutcome.objects.get_or_create(
                    course=crs,
                    number=conum,
                    defaults={"description": codesc}
                )
                if coc:
                    stats["course_outcomes"]["created"] += 1
                else:
                    stats["course_outcomes"]["existing"] += 1

                # Mapping
                copo, copoc = COPOMapping.objects.get_or_create(
                    course_outcome=co,
                    defaults={"mappings": {"1": 3, "2": 2, "3": 2, "13": 3, "14": 2}}
                )
                if copoc:
                    stats["copo_mappings"]["created"] += 1
                else:
                    stats["copo_mappings"]["existing"] += 1

            for rnum, rcit in cdata["refs"]:
                rb, rbc = ReferenceBook.objects.get_or_create(
                    course=crs,
                    number=rnum,
                    defaults={"citation": rcit}
                )
                if rbc:
                    stats["reference_books"]["created"] += 1
                else:
                    stats["reference_books"]["existing"] += 1

        # ── 13. Primary Demonstration Semester (II Year II Semester) ─────────────
        ii_2_courses = [
            {
                "code": "CS2201",
                "title": "Operating Systems",
                "category": cat_objs.get("PCC"),
                "lectures": 3, "tutorials": 0, "practicals": 0, "credits": 3,
                "display_order": 1,
                "prereq_codes": ["CS2102"],
                "syllabus": (
                    "UNIT I: Operating System Overview: System components, OS operations, Resource management, "
                    "User and Operating-System Interface, System calls, System programs, OS structures: Monolithic, "
                    "Layered, Microkernel, Modular approaches. Booting process and Virtual Machines.\n\n"
                    "UNIT II: Process Management & CPU Scheduling: Process concept, Process Control Block (PCB), "
                    "Process state transitions, Threads and multithreading models. CPU Scheduling concepts, Scheduling criteria, "
                    "Algorithms: FCFS, SJF, SRTF, Priority Scheduling, Round Robin, Multi-level Queue and Feedback Queue scheduling.\n\n"
                    "UNIT III: Process Synchronization: Concurrency, Critical Section problem, Peterson's algorithm, "
                    "Hardware support for synchronization (TestAndSet, Swap), Semaphores: Mutex and Counting semaphores, "
                    "Classic IPC problems: Producer-Consumer, Dining Philosophers, Readers-Writers. Monitors.\n\n"
                    "UNIT IV: Deadlocks: System model, Deadlock characterization (Mutual exclusion, Hold & wait, No preemption, "
                    "Circular wait), Resource-allocation graph, Deadlock prevention, Deadlock avoidance: Banker's algorithm, "
                    "Deadlock detection and Recovery from deadlock.\n\n"
                    "UNIT V: Memory Management & Storage: Memory allocation strategies: Paging, Page table structure, "
                    "Segmentation. Virtual Memory: Demand paging, Page replacement algorithms (FIFO, Optimal, LRU, LFU), "
                    "Thrashing. File System interface, Directory structure, Disk scheduling algorithms (FCFS, SSTF, SCAN, C-SCAN)."
                ),
                "cos": [
                    (1, "Explain fundamental operating system concepts, system call architectures, and kernel design models."),
                    (2, "Analyze process scheduling algorithms, thread execution models, and inter-process communication mechanisms."),
                    (3, "Evaluate synchronization primitives, critical section solutions, and deadlock avoidance techniques."),
                    (4, "Analyze contiguous and non-contiguous memory management schemes including virtual memory demand paging."),
                    (5, "Assess file system implementation, directory organizations, and secondary storage disk scheduling policies."),
                ],
                "copo_ratings": [
                    {"1": 3, "2": 2, "12": 2, "13": 3},
                    {"1": 3, "2": 3, "3": 2, "13": 3, "14": 2},
                    {"1": 2, "2": 3, "3": 3, "13": 3},
                    {"1": 3, "2": 3, "3": 2, "13": 2, "14": 2},
                    {"1": 2, "2": 2, "3": 3, "5": 2, "13": 3},
                ],
                "refs": [
                    (1, "Abraham Silberschatz, Peter B. Galvin, Greg Gagne, 'Operating System Concepts', 10th Edition, John Wiley & Sons."),
                    (2, "William Stallings, 'Operating Systems: Internals and Design Principles', 9th Edition, Pearson Education."),
                    (3, "Andrew S. Tanenbaum, Herbert Bos, 'Modern Operating Systems', 4th Edition, Pearson."),
                ]
            },
            {
                "code": "CS2202",
                "title": "Database Management Systems",
                "category": cat_objs.get("PCC"),
                "lectures": 3, "tutorials": 0, "practicals": 0, "credits": 3,
                "display_order": 2,
                "prereq_codes": ["CS2101"],
                "syllabus": (
                    "UNIT I: Introduction & Conceptual Modeling: Database system applications, Purpose of database systems, "
                    "View of data, Database languages (DDL, DML), Database architecture, Database users and administrators. "
                    "Entity-Relationship (ER) model: Entities, Attributes, Relationships, Constraints, Keys, ER diagrams, Extended ER.\n\n"
                    "UNIT II: Relational Model & SQL: Structure of relational databases, Relational algebra operators, "
                    "Tuple relational calculus, SQL data definition, Basic structure of SQL queries, Set operations, "
                    "Aggregate functions, Nested subqueries, Complex queries, Views, Modification of the database, Integrity constraints.\n\n"
                    "UNIT III: Database Design & Normalization: Pitfalls in relational database design, Functional dependencies, "
                    "Closure of functional dependencies, Canonical cover, Normal forms: 1NF, 2NF, 3NF, Boyce-Codd Normal Form (BCNF), "
                    "Lossless decomposition, Dependency preservation, Multi-valued dependencies and 4NF.\n\n"
                    "UNIT IV: Transaction Management & Concurrency Control: Transaction concept, ACID properties, Transaction states, "
                    "Concurrent executions, Serializability: Conflict and View serializability, Recoverability. Lock-based protocols: "
                    "Two-Phase Locking (2PL), Timestamp-based protocols, Validation-based protocols, Deadlock handling.\n\n"
                    "UNIT V: Storage, Indexing & Recovery: File organization, RAID, Indexing: Primary, Secondary, Clustered indexes, "
                    "B-trees and B+ trees index structures, Static and Dynamic hashing. Recovery system: Failure classification, "
                    "Log-based recovery, Write-Ahead Logging (WAL), Checkpoints, Shadow paging."
                ),
                "cos": [
                    (1, "Model enterprise data requirements using conceptual Entity-Relationship diagrams."),
                    (2, "Formulate complex relational algebra and SQL queries with integrity constraints."),
                    (3, "Design normalized relational schemas minimizing redundancy up to BCNF and 4NF."),
                    (4, "Analyze transaction concurrency protocols and serializability control mechanisms."),
                    (5, "Implement indexing and crash-recovery techniques for reliable database persistence."),
                ],
                "copo_ratings": [
                    {"1": 3, "2": 3, "3": 2, "13": 3, "15": 2},
                    {"1": 3, "2": 3, "5": 3, "13": 3, "14": 2},
                    {"1": 2, "2": 3, "3": 3, "13": 3},
                    {"1": 2, "2": 3, "3": 2, "8": 2, "13": 3},
                    {"1": 2, "2": 2, "3": 3, "5": 2, "13": 3, "15": 2},
                ],
                "refs": [
                    (1, "Raghu Ramakrishnan, Johannes Gehrke, 'Database Management Systems', 3rd Edition, McGraw-Hill."),
                    (2, "Abraham Silberschatz, Henry F. Korth, S. Sudarshan, 'Database System Concepts', 7th Edition, McGraw-Hill."),
                    (3, "Ramez Elmasri, Shamkant B. Navathe, 'Fundamentals of Database Systems', 7th Edition, Pearson."),
                ]
            },
            {
                "code": "CS2203",
                "title": "Computer Networks",
                "category": cat_objs.get("PCC"),
                "lectures": 3, "tutorials": 0, "practicals": 0, "credits": 3,
                "display_order": 3,
                "prereq_codes": ["CS2102"],
                "syllabus": (
                    "UNIT I: Introduction to Computer Networks: Network hardware and software, Reference models: OSI and TCP/IP, "
                    "Comparison of models, Physical layer: Transmission media (guided and unguided), Multiplexing (FDM, TDM, WDM), "
                    "Switching techniques: Circuit switching, Packet switching, Virtual circuits.\n\n"
                    "UNIT II: Data Link Layer & MAC: Framing methods, Error detection and correction (Parity, Checksum, CRC, Hamming code), "
                    "Flow control: Stop-and-Wait, Go-Back-N, Selective Repeat. Medium Access Control (MAC) sublayer: Channel allocation, "
                    "Random access protocols: ALOHA, CSMA, CSMA/CD, CSMA/CA. IEEE 802.3 Ethernet standards.\n\n"
                    "UNIT III: Network Layer: Virtual circuit and datagram subnets, Routing algorithms: Shortest path routing, "
                    "Flooding, Distance Vector routing, Link State routing, Hierarchical routing, Congestion control algorithms. "
                    "Internetworking: IPv4 addressing, Subnetting, Classless Inter-Domain Routing (CIDR), NAT, ARP, DHCP, ICMP, IPv6.\n\n"
                    "UNIT IV: Transport Layer: Transport service primitives, Multiplexing and demultiplexing, Connectionless transport (UDP), "
                    "Principles of reliable data transfer, Connection-oriented transport (TCP): Segment structure, Three-way handshake, "
                    "Connection teardown, TCP Flow control, TCP Congestion control (Slow start, Congestion avoidance, Fast retransmit/recovery).\n\n"
                    "UNIT V: Application Layer & Network Security: Domain Name System (DNS), Electronic mail (SMTP, POP3, IMAP), "
                    "World Wide Web (HTTP/HTTPS), File Transfer Protocol (FTP). Basics of Network Security: Symmetric and Asymmetric "
                    "cryptography (AES, RSA), Digital signatures, Firewalls, IPsec, Transport Layer Security (TLS)."
                ),
                "cos": [
                    (1, "Analyze layered network architectures, OSI/TCP-IP models, and physical layer transmission principles."),
                    (2, "Design data link layer framing, error detection, sliding window, and MAC protocols."),
                    (3, "Implement IP subnetting schemes and evaluate interior/exterior routing algorithms."),
                    (4, "Analyze TCP/UDP transport protocols, connection management, and congestion control."),
                    (5, "Assess application layer protocols and foundational network security cryptographic controls."),
                ],
                "copo_ratings": [
                    {"1": 3, "2": 2, "12": 2, "13": 3},
                    {"1": 2, "2": 3, "3": 3, "13": 3},
                    {"1": 3, "2": 3, "3": 2, "13": 3, "14": 2},
                    {"1": 2, "2": 3, "3": 2, "13": 3},
                    {"1": 2, "2": 2, "3": 2, "8": 3, "13": 3, "15": 3},
                ],
                "refs": [
                    (1, "Andrew S. Tanenbaum, David J. Wetherall, 'Computer Networks', 5th Edition, Pearson Education."),
                    (2, "James F. Kurose, Keith W. Ross, 'Computer Networking: A Top-Down Approach', 7th Edition, Pearson."),
                    (3, "Behrouz A. Forouzan, 'Data Communications and Networking', 5th Edition, McGraw-Hill."),
                ]
            },
            {
                "code": "CS2204",
                "title": "Software Engineering",
                "category": cat_objs.get("PCC"),
                "lectures": 3, "tutorials": 0, "practicals": 0, "credits": 3,
                "display_order": 4,
                "prereq_codes": ["CS2103"],
                "syllabus": (
                    "UNIT I: Introduction to Software Engineering: The nature of software, Software process, Generic process model, "
                    "Process assessment and improvement, Prescriptive process models: Waterfall, Incremental, Evolutionary models (Spiral). "
                    "Agile Development: Agile principles, Extreme Programming (XP), Scrum framework, Kanban, User stories.\n\n"
                    "UNIT II: Requirements Engineering: Tasks of requirements engineering, Elicitation, Developing use cases, "
                    "Building the analysis model, Negotiating and validating requirements, Software Requirements Specification (SRS) standard. "
                    "Behavioral modeling, Data flow diagrams, State machine diagrams, UML diagrams.\n\n"
                    "UNIT III: Software Design: Design concepts: Abstraction, Modularity, Information hiding, Cohesion, Coupling. "
                    "Architectural design: Architectural styles and patterns, Component-level design, User Interface Design: "
                    "Interface analysis and design models, Golden rules of UI design.\n\n"
                    "UNIT IV: Software Testing Strategies: Verification and Validation, Unit testing, Integration testing, System testing, "
                    "Acceptance testing. Test techniques: Black-box testing (Equivalence partitioning, Boundary value analysis), "
                    "White-box testing (Basis path testing, Control structure testing). Automated testing and Continuous Integration (CI).\n\n"
                    "UNIT V: Project Management & Quality: Software estimation: LOC, FP, COCOMO II model, Project scheduling, "
                    "Risk management: Risk identification, Projection, Mitigation, Monitoring and Management (RMMM). "
                    "Software Quality Assurance (SQA), Software Configuration Management (SCM), Maintenance and Reengineering."
                ),
                "cos": [
                    (1, "Compare prescriptive software process models with modern Agile Scrum methodologies."),
                    (2, "Elicit, model, and document requirements conforming to IEEE SRS standards."),
                    (3, "Design software architectures applying cohesion, modularity, and architectural patterns."),
                    (4, "Formulate black-box and white-box test cases for structured verification and validation."),
                    (5, "Estimate project metrics, schedule milestones, and apply risk management plans."),
                ],
                "copo_ratings": [
                    {"1": 3, "2": 2, "9": 2, "11": 3, "13": 3},
                    {"1": 2, "2": 3, "3": 3, "10": 2, "13": 3},
                    {"1": 2, "2": 2, "3": 3, "13": 3, "15": 3},
                    {"1": 2, "2": 3, "5": 3, "13": 3},
                    {"1": 2, "2": 2, "8": 2, "9": 3, "11": 3, "13": 3},
                ],
                "refs": [
                    (1, "Roger S. Pressman, Bruce R. Maxim, 'Software Engineering: A Practitioner's Approach', 9th Edition, McGraw-Hill."),
                    (2, "Ian Sommerville, 'Software Engineering', 10th Edition, Pearson Education."),
                    (3, "Pankaj Jalote, 'An Integrated Approach to Software Engineering', 3rd Edition, Narosa Publishing House."),
                ]
            },
            {
                "code": "CS2205",
                "title": "Design and Analysis of Algorithms",
                "category": cat_objs.get("PCC"),
                "lectures": 3, "tutorials": 0, "practicals": 0, "credits": 3,
                "display_order": 5,
                "prereq_codes": ["CS2101"],
                "syllabus": (
                    "UNIT I: Introduction & Analysis Framework: Notion of algorithm, Fundamentals of algorithmic problem solving, "
                    "Space and Time complexity, Asymptotic notations: Big-O, Big-Omega, Big-Theta, Little-o, Little-omega. "
                    "Mathematical analysis of non-recursive and recursive algorithms, Master Theorem for recurrence relations.\n\n"
                    "UNIT II: Divide and Conquer: General method, Applications: Binary search, Merge sort, Quick sort, "
                    "Strassen's matrix multiplication, Finding minimum and maximum, Convex Hull problem. Performance trade-offs.\n\n"
                    "UNIT III: Greedy Method: General method, Knapsack problem, Job sequencing with deadlines, Optimal storage on tapes, "
                    "Huffman coding algorithm, Minimum Cost Spanning Trees: Prim's algorithm, Kruskal's algorithm, Single source shortest paths (Dijkstra's).\n\n"
                    "UNIT IV: Dynamic Programming: Principle of optimality, 0/1 Knapsack problem, Matrix chain multiplication, "
                    "Longest Common Subsequence (LCS), All-Pairs Shortest Paths (Floyd-Warshall algorithm), Optimal Binary Search Trees, "
                    "Traveling Salesperson Problem (TSP).\n\n"
                    "UNIT V: Backtracking, Branch & Bound, NP-Completeness: Backtracking: 8-Queens problem, Sum of subsets, Graph coloring, "
                    "Hamiltonian cycles. Branch and Bound: 0/1 Knapsack, TSP. Introduction to NP-Completeness: P, NP, NP-Hard, NP-Complete classes, Cook's theorem."
                ),
                "cos": [
                    (1, "Analyze time and space asymptotic complexities of recursive and non-recursive algorithms."),
                    (2, "Design optimal Divide-and-Conquer algorithms for sorting, search, and geometric problems."),
                    (3, "Apply Greedy techniques for graph spanning trees, shortest paths, and data compression."),
                    (4, "Formulate Dynamic Programming algorithms for multi-stage computational optimization problems."),
                    (5, "Synthesize Backtracking and Branch-and-Bound algorithms, classifying intractable NP problems."),
                ],
                "copo_ratings": [
                    {"1": 3, "2": 3, "12": 2, "13": 3},
                    {"1": 3, "2": 3, "3": 3, "13": 3},
                    {"1": 2, "2": 3, "3": 3, "13": 3},
                    {"1": 2, "2": 3, "3": 3, "13": 3, "14": 2},
                    {"1": 3, "2": 3, "3": 2, "13": 3},
                ],
                "refs": [
                    (1, "Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein, 'Introduction to Algorithms', 3rd Edition, MIT Press."),
                    (2, "Ellis Horowitz, Sartaj Sahni, Sanguthevar Rajasekaran, 'Fundamentals of Computer Algorithms', 2nd Edition, Universities Press."),
                    (3, "Anany Levitin, 'Introduction to the Design & Analysis of Algorithms', 3rd Edition, Pearson."),
                ]
            },
            {
                "code": "CS2206",
                "title": "Operating Systems Laboratory",
                "category": cat_objs.get("PCC"),
                "lectures": 0, "tutorials": 0, "practicals": 3, "credits": 1.5,
                "display_order": 6,
                "prereq_codes": ["CS2201"],
                "syllabus": (
                    "LIST OF EXPERIMENTS:\n"
                    "1. Basic UNIX/Linux commands, directory operations, file permissions, and shell scripting basics.\n"
                    "2. Implementation of process creation and control using POSIX system calls: fork(), exec(), wait(), exit().\n"
                    "3. Simulation of CPU scheduling algorithms: FCFS, SJF, Priority, and Round Robin.\n"
                    "4. Inter-Process Communication using POSIX shared memory, named pipes (FIFO), and message queues.\n"
                    "5. Implementation of mutual exclusion and synchronization using POSIX semaphores (Producer-Consumer problem).\n"
                    "6. Implementation of the Dining Philosophers synchronization problem using mutex locks and monitors.\n"
                    "7. Simulation of Banker's algorithm for multi-resource deadlock avoidance.\n"
                    "8. Simulation of page replacement algorithms: FIFO, Least Recently Used (LRU), and Optimal.\n"
                    "9. Simulation of disk arm scheduling algorithms: FCFS, SSTF, SCAN, and C-SCAN.\n"
                    "10. Memory allocation algorithms simulation: First Fit, Best Fit, and Worst Fit."
                ),
                "cos": [
                    (1, "Utilize Linux shell environments and process control POSIX system calls."),
                    (2, "Simulate and compare preemptive and non-preemptive CPU scheduling policies."),
                    (3, "Implement concurrent process synchronization and inter-process communication mechanisms."),
                    (4, "Demonstrate deadlock avoidance via multi-resource Banker's algorithm simulation."),
                    (5, "Evaluate virtual memory page replacement and secondary storage disk scheduling efficiency."),
                ],
                "copo_ratings": [
                    {"1": 3, "2": 2, "5": 3, "13": 3},
                    {"1": 2, "2": 3, "3": 2, "5": 3, "13": 3},
                    {"1": 2, "2": 3, "3": 3, "5": 3, "13": 3},
                    {"1": 2, "2": 3, "3": 2, "5": 2, "13": 3},
                    {"1": 2, "2": 2, "3": 2, "5": 3, "13": 3},
                ],
                "refs": [
                    (1, "Silberschatz, Galvin, Gagne, 'Operating System Concepts Essentials', Wiley."),
                    (2, "W. Richard Stevens, Stephen A. Rago, 'Advanced Programming in the UNIX Environment', Addison-Wesley."),
                ]
            },
            {
                "code": "CS2207",
                "title": "Database Management Systems Laboratory",
                "category": cat_objs.get("PCC"),
                "lectures": 0, "tutorials": 0, "practicals": 3, "credits": 1.5,
                "display_order": 7,
                "prereq_codes": ["CS2202"],
                "syllabus": (
                    "LIST OF EXPERIMENTS:\n"
                    "1. Practice of DDL statements: CREATE, ALTER, DROP, TRUNCATE with entity/referential integrity constraints.\n"
                    "2. Practice of DML statements: INSERT, UPDATE, DELETE with transaction COMMIT and ROLLBACK.\n"
                    "3. Queries with relational operators, arithmetic operators, string matching, and ORDER BY / GROUP BY / HAVING clauses.\n"
                    "4. Complex SQL queries using Nested Subqueries, Correlated Subqueries, and Set Operations (UNION, INTERSECT, MINUS).\n"
                    "5. Multi-table joins: Inner Join, Left Outer Join, Right Outer Join, Full Outer Join, and Natural Join.\n"
                    "6. Creation and management of Views, Sequences, Synonyms, and B-Tree Indexes.\n"
                    "7. PL/SQL block programming: Variables, conditional branching, iterative loops.\n"
                    "8. PL/SQL programming using Explicit Cursors, Cursor FOR Loops, and parameterized cursors.\n"
                    "9. Creation and execution of stored Procedures, Functions, and Packages with exception handling.\n"
                    "10. Database Triggers: Row-level and Statement-level BEFORE/AFTER triggers for automated audit logging."
                ),
                "cos": [
                    (1, "Construct normalized relational schemas using DDL commands with integrity constraints."),
                    (2, "Execute complex SQL queries incorporating aggregations, joins, and nested subqueries."),
                    (3, "Design and manage database views, sequences, synonyms, and performance indexes."),
                    (4, "Develop modular PL/SQL stored procedures, functions, packages, and cursor handlers."),
                    (5, "Implement automated audit triggers for transactional data consistency enforcement."),
                ],
                "copo_ratings": [
                    {"1": 3, "2": 2, "5": 3, "13": 3},
                    {"1": 2, "2": 3, "3": 3, "5": 3, "13": 3},
                    {"1": 2, "2": 2, "3": 2, "5": 3, "13": 3},
                    {"1": 2, "2": 3, "3": 3, "5": 3, "13": 3},
                    {"1": 2, "2": 2, "3": 3, "5": 3, "8": 2, "13": 3, "15": 2},
                ],
                "refs": [
                    (1, "Ivan Bayross, 'SQL, PL/SQL: The Programming Language of Oracle', 4th Edition, BPB Publications."),
                    (2, "Raghu Ramakrishnan, Johannes Gehrke, 'Database Management Systems', McGraw-Hill."),
                ]
            },
            {
                "code": "CS2208",
                "title": "Web Technologies Laboratory",
                "category": cat_objs.get("PCC"),
                "lectures": 0, "tutorials": 0, "practicals": 3, "credits": 1.5,
                "display_order": 8,
                "prereq_codes": [],
                "syllabus": (
                    "LIST OF EXPERIMENTS:\n"
                    "1. Design a semantic institutional portal home page using HTML5 structural elements (header, nav, section, footer).\n"
                    "2. Apply advanced CSS3 layout techniques: Flexbox, Grid, custom color variables, and media query responsiveness.\n"
                    "3. Client-side form validation using JavaScript regex patterns, event listeners, and DOM manipulation.\n"
                    "4. Develop dynamic responsive web UI components using modern Bootstrap 5 grid and components.\n"
                    "5. Asynchronous web programming: Fetch API, Promise handling, and parsing JSON responses.\n"
                    "6. Backend server-side web development using Python and Django MVT framework.\n"
                    "7. Model formulation, migration, admin configuration, and dynamic template rendering.\n"
                    "8. User session handling, login authentication, and CSRF security token validation.\n"
                    "9. Development of RESTful web API endpoints for curriculum course management.\n"
                    "10. Full-stack integration: Build an end-to-end database-backed course catalog web application."
                ),
                "cos": [
                    (1, "Design structured, accessible, and responsive user interfaces with HTML5 and CSS3."),
                    (2, "Implement client-side interactive logic and form validations using JavaScript DOM."),
                    (3, "Utilize Bootstrap component libraries and asynchronous JSON data exchange."),
                    (4, "Build backend server-side application routes and database models with Django."),
                    (5, "Deploy secure, end-to-end full-stack web applications with authentication."),
                ],
                "copo_ratings": [
                    {"1": 2, "2": 2, "3": 3, "5": 3, "13": 3},
                    {"1": 2, "2": 3, "3": 3, "5": 3, "13": 3, "14": 2},
                    {"1": 2, "2": 2, "3": 2, "5": 3, "13": 3},
                    {"1": 3, "2": 3, "3": 3, "5": 3, "13": 3, "15": 2},
                    {"1": 2, "2": 2, "3": 3, "5": 3, "8": 2, "9": 2, "13": 3, "15": 3},
                ],
                "refs": [
                    (1, "Jon Duckett, 'HTML and CSS: Design and Build Websites', Wiley."),
                    (2, "David Flanagan, 'JavaScript: The Definitive Guide', 7th Edition, O'Reilly Media."),
                    (3, "William S. Vincent, 'Django for Beginners: Build websites with Python and Django'."),
                ]
            },
            {
                "code": "CS2209",
                "title": "Advanced Python Programming",
                "category": cat_objs.get("DEC"),
                "lectures": 2, "tutorials": 0, "practicals": 2, "credits": 3,
                "display_order": 9,
                "is_elective": True,
                "elective_group": "Professional Elective - I",
                "prereq_codes": [],
                "syllabus": (
                    "UNIT I: Advanced Language Constructs: Function decorators, Class decorators, Generators, "
                    "Iterators, Context managers with 'with' statements, Metaclasses, Magic/Dunder methods, Memory management in Python.\n\n"
                    "UNIT II: Concurrency & Asynchronous Programming: Multithreading with threading module, "
                    "Multiprocessing for CPU-bound tasks, Asynchronous I/O with asyncio, Coroutines, Tasks, and Event Loops.\n\n"
                    "UNIT III: Data Science Stack: NumPy arrays, multidimensional slicing, vectorization. "
                    "Pandas DataFrames, data cleaning, filtering, aggregation, and handling time-series data.\n\n"
                    "UNIT IV: Networking & Web Scraping: Socket programming, HTTP requests with requests module, "
                    "Web scraping using Beautiful Soup and Scrapy, Parsing XML/JSON payloads.\n\n"
                    "UNIT V: Enterprise Development & Testing: Unit testing with unittest and pytest, Mocking, "
                    "Building RESTful APIs with Django REST framework / FastAPI, Packaging and distribution via PyPI."
                ),
                "cos": [
                    (1, "Apply advanced Python language mechanisms including decorators, generators, and metaclasses."),
                    (2, "Develop concurrent and asynchronous applications utilizing threading and asyncio."),
                    (3, "Manipulate and analyze complex tabular datasets using NumPy and Pandas libraries."),
                    (4, "Build network scraping tools and parse structured web data payloads."),
                    (5, "Implement automated test suites and robust REST API services in Python."),
                ],
                "copo_ratings": [
                    {"1": 3, "2": 2, "3": 2, "5": 3, "13": 3},
                    {"1": 2, "2": 3, "3": 3, "5": 3, "13": 3, "14": 2},
                    {"1": 2, "2": 3, "5": 3, "13": 3, "14": 3},
                    {"1": 2, "2": 2, "3": 2, "5": 3, "13": 3},
                    {"1": 2, "2": 2, "3": 3, "5": 3, "13": 3, "15": 2},
                ],
                "refs": [
                    (1, "Luciano Ramalho, 'Fluent Python: Clear, Concise, and Effective Programming', 2nd Edition, O'Reilly."),
                    (2, "David Beazley, Brian K. Jones, 'Python Cookbook', 3rd Edition, O'Reilly Media."),
                ]
            },
            {
                "code": "MC2201",
                "title": "Environmental Science & Constitution of India",
                "category": cat_objs.get("MDC"),
                "lectures": 2, "tutorials": 0, "practicals": 0, "credits": 0,
                "display_order": 10,
                "prereq_codes": [],
                "syllabus": (
                    "UNIT I: Ecosystems & Natural Resources: Concept of ecosystem, structure and function, energy flow. "
                    "Forest, water, mineral, food, and energy resources; Renewable and non-renewable energy sources.\n\n"
                    "UNIT II: Biodiversity & Conservation: Genetic, species, and ecosystem diversity, Hotspots of biodiversity, "
                    "Threats to biodiversity, Endangered and endemic species, In-situ and Ex-situ conservation of biodiversity.\n\n"
                    "UNIT III: Environmental Pollution & Policies: Air, water, soil, noise, and nuclear pollution causes, effects, "
                    "and control measures. Solid waste management, Climate change, Global warming, Ozone layer depletion, Environmental Protection Act.\n\n"
                    "UNIT IV: Constitution of India - Historical Background & Philosophy: Framing of the Constitution, "
                    "Preamble, Fundamental Rights, Fundamental Duties, Directive Principles of State Policy (DPSP).\n\n"
                    "UNIT V: Institutional Governance Structure: Union Government: President, Prime Minister, Parliament, Supreme Court. "
                    "State Government: Governor, Chief Minister, State Legislature, High Courts. Constitutional bodies and Election Commission."
                ),
                "cos": [
                    (1, "Understand ecological systems, natural resource balance, and conservation strategies."),
                    (2, "Assess biodiversity importance and environmental mitigation techniques."),
                    (3, "Analyze pollution control legislation and international environmental protocols."),
                    (4, "Explain foundational constitutional values, fundamental rights, and citizenship duties."),
                    (5, "Appraise union and state governance structures and institutional checks and balances."),
                ],
                "copo_ratings": [
                    {"6": 3, "7": 3, "8": 2},
                    {"6": 2, "7": 3, "8": 2},
                    {"6": 3, "7": 3, "8": 3},
                    {"6": 3, "8": 3},
                    {"6": 3, "8": 3},
                ],
                "refs": [
                    (1, "Erach Bharucha, 'Textbook of Environmental Studies for Undergraduate Courses', Universities Press."),
                    (2, "Dr. B. R. Ambedkar, 'The Constitution of India', Government of India Publication."),
                    (3, "M. Laxmikanth, 'Indian Polity', 6th Edition, McGraw-Hill Education."),
                ]
            },
        ]

        for cdata in ii_2_courses:
            crs, c = Course.objects.get_or_create(
                semester=sem_2_2,
                code=cdata["code"],
                defaults={
                    "title": cdata["title"],
                    "category": cdata["category"],
                    "lectures": cdata["lectures"],
                    "tutorials": cdata["tutorials"],
                    "practicals": cdata["practicals"],
                    "credits": cdata["credits"],
                    "is_elective": cdata.get("is_elective", False),
                    "elective_group": cdata.get("elective_group", ""),
                    "syllabus_text": cdata["syllabus"],
                    "display_order": cdata["display_order"],
                }
            )
            course_lookup[cdata["code"]] = crs
            if c:
                stats["courses"]["created"] += 1
            else:
                stats["courses"]["existing"] += 1
                crs.title = cdata["title"]
                crs.category = cdata["category"]
                crs.syllabus_text = cdata["syllabus"]
                crs.is_elective = cdata.get("is_elective", False)
                crs.elective_group = cdata.get("elective_group", "")
                crs.save()

            # Outcomes
            for idx, (conum, codesc) in enumerate(cdata["cos"]):
                co, coc = CourseOutcome.objects.get_or_create(
                    course=crs,
                    number=conum,
                    defaults={"description": codesc}
                )
                if coc:
                    stats["course_outcomes"]["created"] += 1
                else:
                    stats["course_outcomes"]["existing"] += 1
                    co.description = codesc
                    co.save()

                rating_dict = cdata["copo_ratings"][idx] if idx < len(cdata["copo_ratings"]) else {"1": 2, "2": 2}
                copo, copoc = COPOMapping.objects.get_or_create(
                    course_outcome=co,
                    defaults={"mappings": rating_dict}
                )
                if copoc:
                    stats["copo_mappings"]["created"] += 1
                else:
                    stats["copo_mappings"]["existing"] += 1
                    copo.mappings = rating_dict
                    copo.save()

            # References
            for rnum, rcit in cdata["refs"]:
                rb, rbc = ReferenceBook.objects.get_or_create(
                    course=crs,
                    number=rnum,
                    defaults={"citation": rcit}
                )
                if rbc:
                    stats["reference_books"]["created"] += 1
                else:
                    stats["reference_books"]["existing"] += 1
                    rb.citation = rcit
                    rb.save()

        # ── 14. Connect Prerequisites ────────────────────────────────────────────
        for cdata in ii_2_courses:
            crs = course_lookup.get(cdata["code"])
            if crs and cdata.get("prereq_codes"):
                for pcode in cdata["prereq_codes"]:
                    prereq_crs = course_lookup.get(pcode)
                    if prereq_crs and prereq_crs != crs:
                        crs.prerequisites.add(prereq_crs)

        # ── 15. Pending Change Request for HOD Review Demonstration ──────────────
        se_course = course_lookup.get("CS2204")
        if se_course and faculty_user:
            original_syllabus = se_course.syllabus_text
            proposed_syllabus = (
                original_syllabus + "\n\n"
                "[PROPOSED UPDATE - Unit I]: Added DevOps & Continuous Integration/Continuous "
                "Deployment (CI/CD) pipelines to modern agile workflows. Industry tools: GitHub Actions & Docker."
            )
            cr, c = ChangeRequest.objects.get_or_create(
                curriculum_version=version,
                requested_by=faculty_user,
                model_name="Course",
                record_id=se_course.pk,
                status=ChangeRequest.STATUS_PENDING,
                defaults={
                    "field_changed": "syllabus_text",
                    "old_data": {
                        "code": se_course.code,
                        "title": se_course.title,
                        "syllabus_text": original_syllabus,
                    },
                    "new_data": {
                        "code": se_course.code,
                        "title": se_course.title,
                        "syllabus_text": proposed_syllabus,
                    },
                    "hod_comment": "",
                }
            )
            if c:
                stats["change_requests"]["created"] += 1
                self.stdout.write(self.style.SUCCESS(f"Created Pending ChangeRequest #{cr.pk} for {se_course.code}"))
            else:
                stats["change_requests"]["existing"] += 1

        # ── 16. Historical Audit Trail ───────────────────────────────────────────
        audit_events = [
            (admin_user, AuditLog.ACTION_CREATE, "CurriculumVersion", version.pk, str(version),
             f"Initialized curriculum version for regulation {version.regulation} ({version.academic_year})"),
            (hod_user or admin_user, AuditLog.ACTION_UPDATE, "CurriculumVersion", version.pk, str(version),
             "Configured Department Vision, Mission, and Graduate Attributes"),
            (hod_user or admin_user, AuditLog.ACTION_CREATE, "CourseCategory", None, "PCC",
             "Added course category Professional Core Courses (PCC)"),
            (hod_user or admin_user, AuditLog.ACTION_CREATE, "Course", course_lookup.get("CS2201", se_course).pk, "CS2201 - Operating Systems",
             "Created course CS2201 Operating Systems (3-0-0, 3 credits)"),
            (hod_user or admin_user, AuditLog.ACTION_CREATE, "Course", course_lookup.get("CS2202", se_course).pk, "CS2202 - Database Management Systems",
             "Created course CS2202 Database Management Systems (3-0-0, 3 credits)"),
            (faculty_user or admin_user, AuditLog.ACTION_UPDATE, "CourseOutcome", None, "CO1..CO5 for CS2201",
             "Defined Course Outcomes and Bloom's taxonomy criteria for Operating Systems"),
            (faculty_user or admin_user, AuditLog.ACTION_UPDATE, "COPOMapping", None, "CO-PO Correlation CS2201",
             "Mapped Operating Systems outcomes to NBA Program Outcomes and PSOs"),
            (faculty_user or admin_user, AuditLog.ACTION_UPDATE, "Course", se_course.pk, "CS2204 - Software Engineering",
             "Submitted Change Request for Software Engineering syllabus modernization (DevOps & CI/CD)"),
        ]

        for u, act, mname, recid, rlabel, desc in audit_events:
            if u:
                exists = AuditLog.objects.filter(
                    department=dept,
                    curriculum_version=version,
                    action=act,
                    model_name=mname,
                    description=desc
                ).exists()
                if not exists:
                    AuditLog.objects.create(
                        user=u,
                        department=dept,
                        curriculum_version=version,
                        action=act,
                        model_name=mname,
                        record_id=recid,
                        record_label=rlabel,
                        description=desc
                    )
                    stats["audit_logs"]["created"] += 1
                else:
                    stats["audit_logs"]["existing"] += 1

        # ── 17. Final Summary Output ─────────────────────────────────────────────
        self.stdout.write(self.style.NOTICE("=" * 70))
        self.stdout.write(self.style.SUCCESS("Demo academic data seeding completed successfully!"))
        self.stdout.write(self.style.NOTICE("=" * 70))
        for key, vals in stats.items():
            name = key.replace("_", " ").title()
            self.stdout.write(f"  {name:<24}: Created={vals['created']:<3} | Existing={vals['existing']:<3}")
        self.stdout.write(self.style.NOTICE("=" * 70))
