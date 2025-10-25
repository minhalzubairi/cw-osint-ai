"""
GitHub Data Collector
Collects data from GitHub repositories
"""

from github import Github, GithubException
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

from backend.models.database import CollectedData

logger = logging.getLogger(__name__)


class GitHubCollector:
    """Collector for GitHub repository data"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize GitHub collector
        
        Args:
            config: Configuration dict with 'token' and 'repositories'
        """
        self.token = config.get('token')
        self.repositories = config.get('repositories', [])
        self.client = Github(self.token) if self.token else Github()
    
    async def test_connection(self) -> bool:
        """Test GitHub API connection"""
        try:
            user = self.client.get_user()
            logger.info(f"GitHub connection successful: {user.login}")
            return True
        except GithubException as e:
            logger.error(f"GitHub connection failed: {e}")
            return False
    
    async def collect(self, db, source) -> int:
        """
        Collect data from configured GitHub repositories
        
        Args:
            db: Database session
            source: DataSource model instance
            
        Returns:
            Number of items collected
        """
        collected_count = 0
        since = datetime.utcnow() - timedelta(hours=24)
        
        for repo_name in self.repositories:
            try:
                logger.info(f"Collecting data from {repo_name}")
                repo = self.client.get_repo(repo_name)
                
                # Collect commits
                commits = repo.get_commits(since=since)
                for commit in commits:
                    try:
                        data = CollectedData(
                            source_id=source.id,
                            data_type='commit',
                            external_id=commit.sha,
                            title=commit.commit.message.split('\n')[0][:500],
                            content=commit.commit.message,
                            metadata={
                                'author': commit.commit.author.name if commit.commit.author else None,
                                'additions': commit.stats.additions if commit.stats else 0,
                                'deletions': commit.stats.deletions if commit.stats else 0,
                                'files_changed': len(commit.files) if commit.files else 0
                            },
                            url=commit.html_url,
                            author=commit.commit.author.name if commit.commit.author else None,
                            published_at=commit.commit.author.date if commit.commit.author else None
                        )
                        db.add(data)
                        collected_count += 1
                    except Exception as e:
                        logger.error(f"Error processing commit {commit.sha}: {e}")
                
                # Collect recent issues
                issues = repo.get_issues(state='all', since=since)
                for issue in issues:
                    try:
                        data = CollectedData(
                            source_id=source.id,
                            data_type='issue',
                            external_id=str(issue.number),
                            title=issue.title,
                            content=issue.body or "",
                            metadata={
                                'state': issue.state,
                                'labels': [label.name for label in issue.labels],
                                'comments': issue.comments,
                                'is_pull_request': issue.pull_request is not None
                            },
                            url=issue.html_url,
                            author=issue.user.login if issue.user else None,
                            published_at=issue.created_at
                        )
                        db.add(data)
                        collected_count += 1
                    except Exception as e:
                        logger.error(f"Error processing issue #{issue.number}: {e}")
                
                # Collect pull requests
                pulls = repo.get_pulls(state='all', sort='updated', direction='desc')
                for pr in list(pulls)[:50]:  # Limit to 50 most recent
                    if pr.updated_at < since:
                        break
                    try:
                        data = CollectedData(
                            source_id=source.id,
                            data_type='pull_request',
                            external_id=str(pr.number),
                            title=pr.title,
                            content=pr.body or "",
                            metadata={
                                'state': pr.state,
                                'merged': pr.merged,
                                'additions': pr.additions,
                                'deletions': pr.deletions,
                                'changed_files': pr.changed_files,
                                'comments': pr.comments,
                                'review_comments': pr.review_comments
                            },
                            url=pr.html_url,
                            author=pr.user.login if pr.user else None,
                            published_at=pr.created_at
                        )
                        db.add(data)
                        collected_count += 1
                    except Exception as e:
                        logger.error(f"Error processing PR #{pr.number}: {e}")
                
                db.commit()
                logger.info(f"Collected {collected_count} items from {repo_name}")
                
            except GithubException as e:
                logger.error(f"Error accessing repository {repo_name}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error collecting from {repo_name}: {e}")
        
        return collected_count
    
    def get_repository_stats(self, repo_name: str) -> Dict[str, Any]:
        """Get statistics for a repository"""
        try:
            repo = self.client.get_repo(repo_name)
            return {
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'watchers': repo.watchers_count,
                'open_issues': repo.open_issues_count,
                'language': repo.language,
                'size': repo.size,
                'created_at': repo.created_at.isoformat() if repo.created_at else None,
                'updated_at': repo.updated_at.isoformat() if repo.updated_at else None
            }
        except GithubException as e:
            logger.error(f"Error getting stats for {repo_name}: {e}")
            return {}
