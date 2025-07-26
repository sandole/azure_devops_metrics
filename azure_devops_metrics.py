#!/usr/bin/env python3
"""
Azure DevOps Impact Metrics Script - Simplified Version
Analyzes your contributions across repositories using Azure DevOps REST API
"""

import requests
import json
import base64
from datetime import datetime, timedelta
import argparse
from collections import defaultdict
import urllib3

# Disable SSL warnings for corporate environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AzureDevOpsMetrics:
    def __init__(self, organization, pat, project=None, verify_ssl=True):
        self.organization = organization
        self.project = project
        self.base_url = f"https://dev.azure.com/{organization}"
        self.verify_ssl = verify_ssl
        
        # Encode PAT for authentication
        self.auth_header = {
            'Authorization': f'Basic {base64.b64encode(f":{pat}".encode()).decode()}'
        }
    
    def get_projects(self):
        """Get all projects in the organization"""
        url = f"{self.base_url}/_apis/projects"
        response = requests.get(url, headers=self.auth_header, params={'api-version': '6.0'}, verify=self.verify_ssl)
        if response.status_code == 200:
            return response.json().get('value', [])
        return []
    
    def get_repositories(self, project_id):
        """Get all repositories in a project"""
        url = f"{self.base_url}/{project_id}/_apis/git/repositories"
        response = requests.get(url, headers=self.auth_header, params={'api-version': '6.0'}, verify=self.verify_ssl)
        if response.status_code == 200:
            return response.json().get('value', [])
        return []
    
    def get_commits(self, project_id, repo_id, author_email=None, days_back=90):
        """Get commits by author in the last N days"""
        since_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        url = f"{self.base_url}/{project_id}/_apis/git/repositories/{repo_id}/commits"
        params = {
            'api-version': '6.0',
            'searchCriteria.fromDate': since_date,
            '$top': 1000
        }
        
        # Only add author filter if we have an email
        if author_email and author_email != "unknown@unknown.com":
            params['searchCriteria.author'] = author_email
        
        response = requests.get(url, headers=self.auth_header, params=params, verify=self.verify_ssl)
        if response.status_code == 200:
            commits = response.json().get('value', [])
            
            # If no author email specified, show unique authors for reference
            if not author_email or author_email == "unknown@unknown.com":
                unique_authors = set()
                for commit in commits[:20]:
                    author = commit.get('author', {})
                    email = author.get('email', '')
                    if email and '@' in email:
                        unique_authors.add(email)
                
                if unique_authors:
                    print(f"  📧 Recent authors in this repo: {', '.join(list(unique_authors)[:3])}")
                    
                # If we have a specific email to look for, filter the commits
                if author_email and author_email != "unknown@unknown.com":
                    filtered_commits = []
                    for commit in commits:
                        author = commit.get('author', {})
                        if author.get('email', '').lower() == author_email.lower():
                            filtered_commits.append(commit)
                    return filtered_commits
                
            return commits
        return []
    
    def get_pull_requests(self, project_id, repo_id, days_back=90):
        """Get pull requests in the last N days"""
        url = f"{self.base_url}/{project_id}/_apis/git/repositories/{repo_id}/pullrequests"
        params = {
            'api-version': '6.0',
            'searchCriteria.status': 'all',
            '$top': 1000
        }
        
        response = requests.get(url, headers=self.auth_header, params=params, verify=self.verify_ssl)
        if response.status_code == 200:
            return response.json().get('value', [])
        return []
    
    def get_work_items_assigned(self, project_id, user_email, days_back=90):
        """Get work items assigned to user"""
        if not user_email or user_email == "unknown@unknown.com":
            return []
            
        since_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        wiql_query = {
            "query": f"""
            SELECT [System.Id], [System.Title], [System.State], [System.WorkItemType], [System.CreatedDate]
            FROM WorkItems 
            WHERE [System.AssignedTo] = '{user_email}'
            AND [System.CreatedDate] >= '{since_date}'
            ORDER BY [System.CreatedDate] DESC
            """
        }
        
        url = f"{self.base_url}/{project_id}/_apis/wit/wiql"
        response = requests.post(url, headers={**self.auth_header, 'Content-Type': 'application/json'}, 
                               json=wiql_query, params={'api-version': '6.0'}, verify=self.verify_ssl)
        
        if response.status_code == 200:
            return response.json().get('workItems', [])
        return []
    
    def analyze_metrics(self, days_back=90, user_email=None):
        """Analyze all metrics for the user"""
        print(f"🔍 Analyzing Azure DevOps impact for the last {days_back} days...")
        
        # Test basic connectivity first
        print("🔗 Testing connectivity to Azure DevOps...")
        projects = self.get_projects()
        if not projects:
            print("❌ Could not retrieve projects. Check your organization name and PAT permissions.")
            return
        
        print(f"✅ Successfully connected! Found {len(projects)} projects.")
        
        if user_email:
            print(f"👤 Filtering by email: {user_email}")
        else:
            print("👤 No email filter - showing all activity")
        print("=" * 60)
        
        # Filter projects if specified
        if self.project:
            projects = [p for p in projects if p['name'].lower() == self.project.lower()]
            if not projects:
                print(f"❌ Project '{self.project}' not found!")
                return
        
        total_commits = 0
        total_prs = 0
        total_work_items = 0
        repo_stats = defaultdict(lambda: {'commits': 0, 'prs': 0})
        
        for project in projects:
            project_name = project['name']
            project_id = project['id']
            
            print(f"\n📁 Project: {project_name}")
            
            # Get repositories
            repositories = self.get_repositories(project_id)
            print(f"  Found {len(repositories)} repositories")
            
            for repo in repositories:
                repo_name = repo['name']
                repo_id = repo['id']
                
                # Get commits
                commits = self.get_commits(project_id, repo_id, user_email, days_back)
                
                # Filter commits by email if we have one
                if user_email and user_email != "unknown@unknown.com":
                    filtered_commits = []
                    for commit in commits:
                        author = commit.get('author', {})
                        if author.get('email', '').lower() == user_email.lower():
                            filtered_commits.append(commit)
                    commit_count = len(filtered_commits)
                else:
                    commit_count = len(commits)
                
                total_commits += commit_count
                repo_stats[f"{project_name}/{repo_name}"]['commits'] = commit_count
                
                # Get pull requests (we'll count all PRs for now since filtering by user is complex)
                prs = self.get_pull_requests(project_id, repo_id, days_back)
                pr_count = len(prs)
                total_prs += pr_count
                repo_stats[f"{project_name}/{repo_name}"]['prs'] = pr_count
                
                if commit_count > 0 or pr_count > 0:
                    print(f"  📂 {repo_name}: {commit_count} commits, {pr_count} PRs (all users)")
            
            # Get work items
            work_items = self.get_work_items_assigned(project_id, user_email, days_back)
            work_item_count = len(work_items)
            total_work_items += work_item_count
            
            if work_item_count > 0:
                print(f"  📋 Work Items assigned to you: {work_item_count}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 SUMMARY METRICS")
        print("=" * 60)
        if user_email and user_email != "unknown@unknown.com":
            print(f"📝 Your Commits: {total_commits}")
        else:
            print(f"📝 Total Commits (all users): {total_commits}")
        print(f"🔄 Total Pull Requests (all users): {total_prs}")
        print(f"📋 Work Items assigned to you: {total_work_items}")
        
        # Top repositories by activity
        if repo_stats:
            print(f"\n🏆 Most Active Repositories:")
            sorted_repos = sorted(repo_stats.items(), 
                                key=lambda x: x[1]['commits'] + x[1]['prs'], 
                                reverse=True)[:10]
            
            for repo, stats in sorted_repos:
                total_activity = stats['commits'] + stats['prs']
                if total_activity > 0:
                    print(f"  • {repo}: {stats['commits']} commits, {stats['prs']} PRs")
        
        print(f"\n⏰ Analysis period: Last {days_back} days")
        print(f"📅 Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    parser = argparse.ArgumentParser(description='Analyze Azure DevOps impact metrics')
    parser.add_argument('--organization', '-o', required=True, 
                       help='Azure DevOps organization name')
    parser.add_argument('--pat', '-p', required=True,
                       help='Personal Access Token')
    parser.add_argument('--project', '-pr', 
                       help='Specific project name (optional)')
    parser.add_argument('--days', '-d', type=int, default=90,
                       help='Number of days to look back (default: 90)')
    parser.add_argument('--no-ssl-verify', action='store_true',
                       help='Disable SSL certificate verification (for corporate firewalls)')
    parser.add_argument('--email', '-e', 
                       help='Your email address for filtering commits and work items')
    
    args = parser.parse_args()
    
    analyzer = AzureDevOpsMetrics(args.organization, args.pat, args.project, not args.no_ssl_verify)
    analyzer.analyze_metrics(args.days, args.email)

if __name__ == "__main__":
    main()