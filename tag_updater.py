import json
import planning_domains_api as api
import ast

# Pull requirments from precomputed json file
f = open("processed_result5.json")
processed_requirements = json.load(f)

DEBUG = True

def update_tags(resource, id, *, current, required):
    assert resource in ["collection", "domain", "problem"]   

    # Remove incorrect tags
    for tag in current:
        if tag not in required:
            if DEBUG:
                print(f"Untagging {tag} from {resource}: {id}")
            elif resource == "collection":
                api.untag_collection(id, tag)
            elif resource == "domain":
                api.untag_domain(id, tag)
            elif resource == "problem":
                api.untag_problem(id, tag)

    # Add required tags
    for tag in required:
        if tag not in current:
            if DEBUG:
                print(f"Tagging {tag} from {resource}: {id}")
            elif resource == "collection":
                api.tag_collection(id, tag)
            elif resource == "domain":
                api.tag_domain(id, tag)
            elif resource == "problem":
                api.tag_problem(id, tag)

collections = api.get_collections()
for collection in collections:
    collection_id = int(collection["collection_id"])

    # Keep track of all requirements inside this collection
    collection_required_tags = set()

    domains = api.get_domains(collection_id)
    assert ast.literal_eval(collection['domain_set']).sort() == [x['domain_id'] for x in domains].sort(), "domain_set property should contain all domains"
    for domain in domains:
        domain_id = domain['domain_id']

        # pull pre-computed domain requirements
        required_tags = processed_requirements[str(domain_id)]['val']

        domain_current_tags = ast.literal_eval(domain['tags'])
        update_tags("domain", domain_id, current=domain_current_tags, required=required_tags)

        # Update collection_required_tags with the union of itself and this domain's requirements
        collection_required_tags.update(required_tags)

        problems = api.get_problems(domain_id)
        for problem in problems:
            problem_current_tags = ast.literal_eval(problem['tags'])
            update_tags("problem", problem['problem_id'], current=problem_current_tags, required=required_tags)

    collection_current_tags = ast.literal_eval(collection['tags'])
    update_tags("domain", domain_id, current=collection_current_tags, required=list(collection_required_tags))